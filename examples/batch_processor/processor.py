"""
Batch Processor for Claude API

Efficiently process multiple prompts concurrently with error recovery,
progress tracking, and results export.

Features:
- Concurrent processing with thread pool
- Progress tracking with tqdm
- Error recovery and retry logic
- Results export (JSON, CSV)
- Rate limiting
- Detailed logging

Usage:
    python processor.py input.json output.json
    python processor.py input.csv output.csv --format csv --workers 4
"""

import argparse
import csv
import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from tqdm import tqdm

from claude_oauth_auth import ClaudeClient


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("batch_processor.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class ProcessingResult:
    """Result of processing a single prompt."""
    index: int
    prompt: str
    response: Optional[str] = None
    success: bool = False
    error: Optional[str] = None
    duration: float = 0.0
    retries: int = 0


class BatchProcessor:
    """
    Batch processor for Claude API with concurrency and error handling.

    Features:
    - Concurrent processing with configurable workers
    - Automatic retry on failures
    - Rate limiting
    - Progress tracking
    - Multiple output formats
    """

    def __init__(
        self,
        max_workers: int = 3,
        max_retries: int = 2,
        retry_delay: float = 1.0,
        rate_limit: Optional[float] = None,
        verbose: bool = False
    ):
        """
        Initialize batch processor.

        Args:
            max_workers: Number of concurrent workers
            max_retries: Maximum retry attempts per prompt
            retry_delay: Delay between retries in seconds
            rate_limit: Minimum seconds between requests (rate limiting)
            verbose: Enable verbose logging
        """
        self.max_workers = max_workers
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.rate_limit = rate_limit
        self.verbose = verbose

        # Initialize Claude client
        try:
            self.client = ClaudeClient(verbose=verbose)
            logger.info("Claude client initialized successfully")
        except ValueError as e:
            logger.error(f"Failed to initialize Claude client: {e}")
            raise

        # Track last request time for rate limiting
        self.last_request_time = 0.0

    def _enforce_rate_limit(self) -> None:
        """Enforce rate limiting between requests."""
        if self.rate_limit is not None:
            elapsed = time.time() - self.last_request_time
            if elapsed < self.rate_limit:
                time.sleep(self.rate_limit - elapsed)
        self.last_request_time = time.time()

    def process_single(
        self,
        index: int,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> ProcessingResult:
        """
        Process a single prompt with retry logic.

        Args:
            index: Prompt index
            prompt: The prompt text
            max_tokens: Optional max tokens override
            temperature: Optional temperature override

        Returns:
            ProcessingResult with outcome
        """
        retries = 0
        start_time = time.time()

        while retries <= self.max_retries:
            try:
                # Enforce rate limiting
                self._enforce_rate_limit()

                # Build kwargs
                kwargs = {}
                if max_tokens is not None:
                    kwargs["max_tokens"] = max_tokens
                if temperature is not None:
                    kwargs["temperature"] = temperature

                # Generate response
                response = self.client.generate(prompt, **kwargs)
                duration = time.time() - start_time

                return ProcessingResult(
                    index=index,
                    prompt=prompt,
                    response=response,
                    success=True,
                    duration=duration,
                    retries=retries
                )

            except Exception as e:
                logger.warning(f"Error processing prompt {index} (attempt {retries + 1}): {e}")
                retries += 1

                if retries <= self.max_retries:
                    time.sleep(self.retry_delay * retries)  # Exponential backoff
                else:
                    duration = time.time() - start_time
                    return ProcessingResult(
                        index=index,
                        prompt=prompt,
                        success=False,
                        error=str(e),
                        duration=duration,
                        retries=retries - 1
                    )

        # Should not reach here, but just in case
        return ProcessingResult(
            index=index,
            prompt=prompt,
            success=False,
            error="Max retries exceeded",
            duration=time.time() - start_time,
            retries=self.max_retries
        )

    def process_batch(
        self,
        prompts: List[Dict[str, Any]],
        show_progress: bool = True
    ) -> List[ProcessingResult]:
        """
        Process multiple prompts concurrently.

        Args:
            prompts: List of prompt dictionaries with keys:
                    - prompt: The prompt text (required)
                    - max_tokens: Optional max tokens
                    - temperature: Optional temperature
            show_progress: Show progress bar

        Returns:
            List of ProcessingResult objects
        """
        results: List[Optional[ProcessingResult]] = [None] * len(prompts)

        # Create progress bar
        pbar = tqdm(total=len(prompts), desc="Processing", disable=not show_progress)

        # Process concurrently
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            futures = {}
            for i, prompt_data in enumerate(prompts):
                future = executor.submit(
                    self.process_single,
                    i,
                    prompt_data["prompt"],
                    prompt_data.get("max_tokens"),
                    prompt_data.get("temperature")
                )
                futures[future] = i

            # Collect results as they complete
            for future in as_completed(futures):
                index = futures[future]
                try:
                    result = future.result()
                    results[index] = result

                    if result.success:
                        pbar.set_postfix({"success": "✓", "retries": result.retries})
                    else:
                        pbar.set_postfix({"success": "✗", "error": result.error[:30]})

                except Exception as e:
                    logger.error(f"Unexpected error processing prompt {index}: {e}")
                    results[index] = ProcessingResult(
                        index=index,
                        prompt=prompts[index]["prompt"],
                        success=False,
                        error=f"Unexpected error: {e}"
                    )

                pbar.update(1)

        pbar.close()

        # Filter out None values (shouldn't happen, but be safe)
        return [r for r in results if r is not None]

    def save_results_json(self, results: List[ProcessingResult], output_path: Path) -> None:
        """Save results to JSON file."""
        data = [asdict(r) for r in results]
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)
        logger.info(f"Results saved to {output_path}")

    def save_results_csv(self, results: List[ProcessingResult], output_path: Path) -> None:
        """Save results to CSV file."""
        with open(output_path, "w", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=["index", "prompt", "response", "success", "error", "duration", "retries"]
            )
            writer.writeheader()
            for result in results:
                writer.writerow(asdict(result))
        logger.info(f"Results saved to {output_path}")

    def print_summary(self, results: List[ProcessingResult]) -> None:
        """Print summary statistics."""
        total = len(results)
        successful = sum(1 for r in results if r.success)
        failed = total - successful
        avg_duration = sum(r.duration for r in results) / total if total > 0 else 0
        total_retries = sum(r.retries for r in results)

        print("\n" + "=" * 60)
        print("BATCH PROCESSING SUMMARY")
        print("=" * 60)
        print(f"Total prompts:     {total}")
        print(f"Successful:        {successful} ({successful/total*100:.1f}%)")
        print(f"Failed:            {failed} ({failed/total*100:.1f}%)")
        print(f"Average duration:  {avg_duration:.2f}s")
        print(f"Total retries:     {total_retries}")
        print("=" * 60 + "\n")


def load_prompts_from_json(file_path: Path) -> List[Dict[str, Any]]:
    """Load prompts from JSON file."""
    with open(file_path) as f:
        data = json.load(f)

    # Handle different JSON structures
    if isinstance(data, list):
        # List of strings or dicts
        prompts = []
        for item in data:
            if isinstance(item, str):
                prompts.append({"prompt": item})
            elif isinstance(item, dict):
                prompts.append(item)
        return prompts
    elif isinstance(data, dict) and "prompts" in data:
        # {"prompts": [...]}
        return data["prompts"]
    else:
        raise ValueError("Invalid JSON structure. Expected list or {prompts: [...]}")


def load_prompts_from_csv(file_path: Path) -> List[Dict[str, Any]]:
    """Load prompts from CSV file."""
    prompts = []
    with open(file_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            prompt_data = {"prompt": row["prompt"]}
            if "max_tokens" in row and row["max_tokens"]:
                prompt_data["max_tokens"] = int(row["max_tokens"])
            if "temperature" in row and row["temperature"]:
                prompt_data["temperature"] = float(row["temperature"])
            prompts.append(prompt_data)
    return prompts


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Batch process multiple prompts using Claude API"
    )
    parser.add_argument("input", type=Path, help="Input file (JSON or CSV)")
    parser.add_argument("output", type=Path, help="Output file (JSON or CSV)")
    parser.add_argument(
        "--format",
        choices=["json", "csv"],
        help="Output format (auto-detected from extension if not specified)"
    )
    parser.add_argument("--workers", type=int, default=3, help="Number of concurrent workers")
    parser.add_argument("--retries", type=int, default=2, help="Max retries per prompt")
    parser.add_argument("--retry-delay", type=float, default=1.0, help="Delay between retries")
    parser.add_argument("--rate-limit", type=float, help="Min seconds between requests")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Determine output format
    output_format = args.format
    if not output_format:
        output_format = args.output.suffix[1:]  # Remove leading dot
        if output_format not in ["json", "csv"]:
            output_format = "json"

    # Load prompts
    logger.info(f"Loading prompts from {args.input}")
    if args.input.suffix == ".json":
        prompts = load_prompts_from_json(args.input)
    elif args.input.suffix == ".csv":
        prompts = load_prompts_from_csv(args.input)
    else:
        logger.error("Input file must be .json or .csv")
        return

    logger.info(f"Loaded {len(prompts)} prompts")

    # Create processor
    processor = BatchProcessor(
        max_workers=args.workers,
        max_retries=args.retries,
        retry_delay=args.retry_delay,
        rate_limit=args.rate_limit,
        verbose=args.verbose
    )

    # Process batch
    logger.info("Starting batch processing...")
    results = processor.process_batch(prompts)

    # Save results
    if output_format == "csv":
        processor.save_results_csv(results, args.output)
    else:
        processor.save_results_json(results, args.output)

    # Print summary
    processor.print_summary(results)


if __name__ == "__main__":
    main()
