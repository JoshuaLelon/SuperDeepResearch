#!/usr/bin/env python3
import asyncio
import sys
import os
import logging
import time
from patchright.async_api import async_playwright
from rich.logging import RichHandler
from rich.console import Console
from rich import print as rprint

# Configure logging with rich
console = Console()
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True, console=console)]
)

logger = logging.getLogger("gemini_research")

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_server.tools.gemini_research import load_config

def log_step(message, status="started"):
    """Log a step with timestamp and status."""
    timestamp = time.strftime("%H:%M:%S")
    if status == "started":
        rprint(f"[bold blue][{timestamp}] ⏳ {message}...[/bold blue]")
    elif status == "completed":
        rprint(f"[bold green][{timestamp}] ✅ {message}[/bold green]")
    elif status == "failed":
        rprint(f"[bold red][{timestamp}] ❌ {message}[/bold red]")
    elif status == "warning":
        rprint(f"[bold yellow][{timestamp}] ⚠️ {message}[/bold yellow]")

async def main():
    browser = None
    try:
        # Load config
        log_step("Loading configuration")
        config = load_config()
        log_step("Configuration loaded", "completed")
        
        log_step("Initializing browser")
        async with async_playwright() as p:
            # Launch browser with undetectable settings
            log_step("Launching browser with undetectable settings")
            browser = await p.chromium.launch(
                headless=False,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--disable-software-rasterizer',
                    '--disable-extensions',
                    '--disable-blink-features=AutomationControlled',  # Hide automation
                    '--disable-automation',  # Disable automation flags
                    '--disable-web-security',  # Allow cross-origin requests
                    '--disable-features=IsolateOrigins,site-per-process'  # Disable site isolation
                ]
            )
            log_step("Browser launched successfully", "completed")
            
            # Create a new context with undetectable settings
            log_step("Creating browser context with undetectable settings")
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},  # Standard resolution
                java_script_enabled=True,
                bypass_csp=True,  # Bypass Content Security Policy
                ignore_https_errors=True,
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'  # Latest Chrome UA
            )
            log_step("Browser context created", "completed")
            
            # Add evasion scripts
            log_step("Adding evasion scripts")
            await context.add_init_script("""
                // Overwrite navigator.webdriver
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                
                // Add missing chrome properties
                window.chrome = {
                    runtime: {}
                };
                
                // Add missing permissions
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                    Promise.resolve({state: Notification.permission}) :
                    originalQuery(parameters)
                );
            """)
            log_step("Evasion scripts added", "completed")
            
            # Create a new page
            log_step("Creating new page")
            page = await context.new_page()
            log_step("Page created", "completed")
            
            log_step("Navigating to Gemini")
            await page.goto('https://gemini.google.com/app', wait_until='networkidle')
            log_step("Navigation completed", "completed")
            
            try:
                log_step("Looking for sign in button")
                await page.wait_for_selector('button:has-text("Sign in")', timeout=5000)
                await page.click('button:has-text("Sign in")')
                await page.wait_for_load_state('networkidle')
                log_step("Sign in button clicked", "completed")
                
                log_step("Looking for email input field")
                await page.wait_for_selector('input[type="email"]', timeout=5000)
                # Type like a human with random delays
                log_step("Entering email")
                await page.fill('input[type="email"]', config.google_email, delay=100)
                await page.keyboard.press('Enter')
                await page.wait_for_load_state('networkidle')
                log_step("Email entered", "completed")
                
                log_step("Looking for password input field")
                await page.wait_for_selector('input[type="password"]', timeout=5000)
                # Type like a human with random delays
                log_step("Entering password")
                await page.fill('input[type="password"]', config.google_password, delay=100)
                await page.keyboard.press('Enter')
                await page.wait_for_load_state('networkidle')
                log_step("Password entered", "completed")
                
                log_step("Waiting for login completion")
                await page.wait_for_timeout(5000)
                log_step("Login completed", "completed")
                
                log_step("Looking for model selector")
                await page.wait_for_selector('text=Gemini 1.5 Pro with Deep Research', timeout=5000)
                await page.click('text=Gemini 1.5 Pro with Deep Research')
                await page.wait_for_timeout(1000)
                log_step("Model selected", "completed")
                
                log_step("Looking for Try Now button")
                await page.wait_for_selector('button:has-text("Try Now")', timeout=5000)
                await page.click('button:has-text("Try Now")')
                await page.wait_for_timeout(2000)
                log_step("Try Now clicked", "completed")
                
                log_step("Looking for query input")
                await page.wait_for_selector('textarea', timeout=5000)
                # Type like a human with random delays
                log_step(f"Entering query: {sys.argv[1][:50]}...")
                await page.fill('textarea', sys.argv[1], delay=50)
                await page.keyboard.press('Enter')
                log_step("Query entered", "completed")
                
                log_step("Waiting for response")
                await page.wait_for_timeout(10000)
                
                log_step("Looking for response content")
                response_content = await page.query_selector('.response-content')
                if response_content:
                    text = await response_content.text_content()
                    log_step("Response received", "completed")
                    console.print("\n[bold cyan]Research Results:[/bold cyan]")
                    console.print(text)
                else:
                    log_step("No response content found", "warning")
                
            except Exception as e:
                log_step(f"Error during interaction: {str(e)}", "failed")
                # Take screenshot on error for debugging
                screenshot_path = 'error.png'
                await page.screenshot(path=screenshot_path)
                log_step(f"Error screenshot saved to {screenshot_path}", "warning")
                
            log_step("Cleaning up browser resources")
            await context.close()
            await browser.close()
            log_step("Browser resources cleaned up", "completed")
            
    except Exception as e:
        log_step(f"Fatal error: {str(e)}", "failed")
        raise
    finally:
        if browser:
            log_step("Stopping browser")
            try:
                await browser.close()
                log_step("Browser stopped", "completed")
            except:
                log_step("Error stopping browser", "failed")

if __name__ == '__main__':
    console.print("[bold magenta]Starting Gemini research with Patchright...[/bold magenta]")
    asyncio.run(main())
    console.print("[bold magenta]Research completed[/bold magenta]") 