#!/usr/bin/env python3
"""
Script to start the BlackMamba Cognitive Core API server
"""
import uvicorn
import argparse
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from blackmamba.utils.config import config


def main():
    """Start the API server"""
    parser = argparse.ArgumentParser(description="Start BlackMamba Cognitive Core API")
    parser.add_argument(
        "--host",
        default=config.api_host,
        help=f"Host to bind to (default: {config.api_host})"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=config.api_port,
        help=f"Port to bind to (default: {config.api_port})"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        default=config.api_reload,
        help="Enable auto-reload for development"
    )
    parser.add_argument(
        "--log-level",
        default=config.log_level.lower(),
        choices=["debug", "info", "warning", "error", "critical"],
        help=f"Log level (default: {config.log_level.lower()})"
    )
    
    args = parser.parse_args()
    
    print(f"""
    ╔══════════════════════════════════════════════════════════╗
    ║  BlackMamba Cognitive Core API                           ║
    ║  Motor cognitivo modular para IA                         ║
    ╚══════════════════════════════════════════════════════════╝
    
    Starting API server...
    Host: {args.host}
    Port: {args.port}
    Reload: {args.reload}
    Log Level: {args.log_level.upper()}
    
    API Documentation: http://{args.host}:{args.port}/docs
    Health Check: http://{args.host}:{args.port}/health
    """)
    
    # Create data directory if it doesn't exist
    os.makedirs("./data", exist_ok=True)
    
    uvicorn.run(
        "blackmamba.api.app:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level=args.log_level
    )


if __name__ == "__main__":
    main()
