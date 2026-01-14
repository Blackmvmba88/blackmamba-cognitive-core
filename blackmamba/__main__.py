"""
Main entry point for running BlackMamba Cognitive Core as a module
"""

import uvicorn
from blackmamba.utils.config import config


def main():
    """Run the API server"""
    print(
        """
    ╔══════════════════════════════════════════════════════════╗
    ║  BlackMamba Cognitive Core                               ║
    ║  Motor cognitivo modular para IA                         ║
    ╚══════════════════════════════════════════════════════════╝
    """
    )

    uvicorn.run(
        "blackmamba.api.app:app",
        host=config.api_host,
        port=config.api_port,
        reload=config.api_reload,
        log_level=config.log_level.lower(),
    )


if __name__ == "__main__":
    main()
