"""
Browser automation for Gemini research
"""
from typing import Optional
import logging
from browser_use import Agent, BrowserConfig, Browser, BrowserContextConfig
from langchain_openai import ChatOpenAI
from .config import Config

logger = logging.getLogger(__name__)

class GeminiAutomation:
    """Handles browser automation for Gemini research"""
    
    def __init__(self, config: Config):
        self.config = config
        self.llm = ChatOpenAI(model="gpt-4o")
        self.gemini_url = "https://gemini.google.com/app"
        self.agent = None
        
    async def setup_browser(self):
        """Initialize browser with configuration"""
        logger.info("Setting up browser...")
        context_config = BrowserContextConfig(
            browser_window_size={'width': 1920, 'height': 1080},
            wait_for_network_idle_page_load_time=3.0
        )
        
        browser_config = BrowserConfig(
            headless=self.config.research_preferences.headless,
            disable_security=True,
            new_context_config=context_config
        )
        
        logger.info(f"Browser mode: {'headless' if self.config.research_preferences.headless else 'visible'}")
        browser = Browser(config=browser_config)
        return browser

    async def research_topic(self, query: str) -> str:
        """Conduct research on a given topic using Gemini"""
        browser = None
        try:
            logger.info(f"Starting research on query: {query}")
            task = (
                f"Complete the following sequence of actions:\n\n"
                f"1. Go to {self.gemini_url}\n"
                f"2. Wait for the page to load completely\n"
                f"3. If you see a 'Sign in' button, click it\n"
                f"4. If on the Google sign-in page:\n"
                f"   - Enter email: {self.config.google_email}\n"
                f"   - Click Next\n"
                f"   - Enter password: {self.config.google_password}\n"
                f"   - Click Next\n"
                f"   - Wait for me to finish two-step verification\n"
                f"5. Once signed in, look for and click on the model selector dropdown\n"
                f"6. Select 'Gemini 1.5 Pro with Deep Research' from the dropdown\n"
                f"7. Wait for the model to be selected\n"
                f"8. Click Try Now\n"
                f"9. In the input field, type the following query:\n"
                f"   {query}\n"
                f"10. Press Enter or click the send button\n"
                f"11. Wait for the response to complete\n"
                f"12. Click Edit Plan\n"
                f"13. Type the following:\n"
                f"   {query}\n"
                f"14. Press Enter\n"
                f"15. Wait for the response to complete\n"
                f"16. Extract and return the complete response text\n\n"
                f"Important Notes:\n"
                f"- Handle any 2FA or security prompts if they appear\n"
                f"- Ensure the model is set to Gemini 1.5 Pro with Deep Research before proceeding\n"
                f"- Wait for complete response before extracting\n"
                f"- Include any citations or references in the response\n"
                f"- After each action, print a detailed message describing what you just did\n"
            )

            if not self.config.google_email or not self.config.google_password:
                raise ValueError("Google credentials not found in config. Please set GOOGLE_EMAIL and GOOGLE_PASSWORD environment variables.")

            logger.info("Initializing browser...")
            browser = await self.setup_browser()
            
            logger.info("Setting up research agent...")
            if not self.agent:
                self.agent = Agent(
                    task=task,
                    llm=self.llm,
                    browser=browser,
                    generate_gif=False,
                    max_input_tokens=32000,
                    max_actions_per_step=3
                )
            else:
                self.agent.task = task
                self.agent.browser = browser

            logger.info("Starting research automation...")
            result = await self.agent.run(max_steps=15)  # Increased max_steps to account for sign-in
            logger.info("Research completed successfully")
            return result.final_result() or "No results found"

        except Exception as e:
            logger.error(f"Failed to conduct research: {str(e)}")
            return f"Research failed: {str(e)}"
        
        finally:
            if browser:
                logger.info("Closing browser...")
                await browser.close()

    async def close(self):
        """Close browser"""
        logger.info("Cleaning up resources...")
        # The Agent class handles cleanup automatically 