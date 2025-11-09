"""Expose the existing CLI entrypoint for `python -m fm_skin_builder`."""

from src.cli.main import entrypoint


def main() -> None:
  """Delegate to the real CLI entrypoint."""
  entrypoint()


__all__ = ["main", "entrypoint"]
