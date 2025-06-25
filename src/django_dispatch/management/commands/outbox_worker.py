import logging
import signal
import time
from django.core.management.base import BaseCommand
from django_dispatch.publishers import publisher

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Run the outbox pattern worker to process pending events'

    def __init__(self):
        super().__init__()
        self.running = True

    def add_arguments(self, parser):
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Number of events to process in each batch (default: 100)'
        )
        parser.add_argument(
            '--interval',
            type=int,
            default=5,
            help='Interval in seconds between processing batches (default: 5)'
        )
        parser.add_argument(
            '--max-iterations',
            type=int,
            default=0,
            help='Maximum number of iterations to run (0 for infinite, default: 0)'
        )

    def handle(self, *args, **options):
        batch_size = options['batch_size']
        interval = options['interval']
        max_iterations = options['max_iterations']

        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        self.stdout.write(
            self.style.SUCCESS(
                f'Starting outbox worker (batch_size={batch_size}, interval={interval}s)'
            )
        )

        iteration = 0

        while self.running:
            try:
                # Check backend health
                health_status = publisher.get_backend_health()
                unhealthy_backends = [name for name, healthy in health_status.items() if not healthy]

                if unhealthy_backends:
                    logger.warning(f"Unhealthy backends detected: {unhealthy_backends}")

                # Process pending events
                processed_count = publisher.process_pending_events(batch_size)

                if processed_count > 0:
                    self.stdout.write(
                        self.style.SUCCESS(f'Processed {processed_count} events')
                    )
                    logger.info(f"Processed {processed_count} events in iteration {iteration + 1}")
                else:
                    logger.debug(f"No events to process in iteration {iteration + 1}")

                iteration += 1

                # Check if we've reached max iterations
                if max_iterations > 0 and iteration >= max_iterations:
                    self.stdout.write(
                        self.style.SUCCESS(f'Reached maximum iterations ({max_iterations}), stopping')
                    )
                    break

                # Wait before next iteration
                if self.running:
                    time.sleep(interval)

            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Error in outbox worker: {str(e)}")
                self.stdout.write(
                    self.style.ERROR(f'Error in worker: {str(e)}')
                )
                # Continue running even if there's an error
                time.sleep(interval)

        self.stdout.write(
            self.style.SUCCESS('Outbox worker stopped gracefully')
        )

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.stdout.write(
            self.style.WARNING(f'Received signal {signum}, shutting down gracefully...')
        )
        self.running = False
