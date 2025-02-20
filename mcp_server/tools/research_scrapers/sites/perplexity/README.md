# Perplexity Scraper Documentation

This document details our attempts to automate access to Perplexity, including various approaches, challenges, and outcomes.

## Browser Configuration Attempts

### 1. Basic Browser Launch
Initial attempt with minimal configuration:
```python
browser = await patchright.chromium.launch(headless=False)
```
Result: Detected and blocked by Perplexity's anti-automation measures.

### 2. Enhanced Browser Arguments
Added anti-detection arguments:
```python
browser = await patchright.chromium.launch(
    headless=False,
    args=[
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu',
        '--disable-software-rasterizer',
        '--disable-extensions',
        '--disable-blink-features=AutomationControlled',
        '--disable-automation',
        '--disable-web-security',
        '--disable-features=IsolateOrigins,site-per-process',
        '--enable-javascript',
        '--window-size=1920,1080'
    ]
)
```
Result: Still detected, but improved success rate.

### 3. Browser Context Configuration
Added realistic browser context:
```python
context = await browser.new_context(
    viewport={'width': 1920, 'height': 1080},
    java_script_enabled=True,
    bypass_csp=True,
    ignore_https_errors=True,
    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    extra_http_headers={
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1'
    }
)
```
Result: Improved evasion but still inconsistent.

## Google Login Button Interaction Attempts

### 1. Basic Click Approach
Initial attempt to click the Google login button:
```python
google_button = await page.wait_for_selector('button:has-text("Continue with Google")')
await google_button.click()
```
Error:
```
TimeoutError: Timeout 30000ms exceeded while waiting for event "popup"
```

### 2. Force Click with Evaluation
Attempted to force click using JavaScript:
```python
await page.evaluate('''() => {
    const buttons = Array.from(document.querySelectorAll('button'));
    const googleButton = buttons.find(btn => 
        btn.textContent.includes('Continue with Google')
    );
    if (googleButton) {
        googleButton.click();
    }
}''')
```
Error:
```
Error during Google login: Page.goto: net::ERR_ABORTED; maybe frame was detached?
```

### 3. Overlay Removal Approach
Tried removing potential overlays:
```python
await page.evaluate('''() => {
    document.querySelectorAll('div[class*="overlay"], div[class*="modal"]').forEach(el => {
        el.style.zIndex = '-1';
        el.style.pointerEvents = 'none';
    });
}''')
```
Result: Button became clickable but popup still failed to open.

### 4. Human-like Interaction
Added mouse movement and delays:
```python
box = await google_button.bounding_box()
await page.mouse.move(
    box['x'] + box['width'] / 2,
    box['y'] + box['height'] / 2,
    steps=10
)
await asyncio.sleep(0.1)
await google_button.click()
```
Error:
```
Error during Google login: Page.goto: Timeout 30000ms exceeded.
Call log:
  - navigating to "https://accounts.google.com/", waiting until "load"
```

### 5. Direct Navigation Attempt
Tried creating new page and navigating directly:
```python
context = page.context
google_page = await context.new_page()
await google_page.goto('https://accounts.google.com')
```
Error:
```
Error during Google login: Page.goto: net::ERR_ABORTED; maybe frame was detached?
```

## Browser Fingerprint Evasion Attempts

### 1. Basic WebDriver Removal
```python
await page.evaluate('''() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
}''')
```
Result: Basic detection bypassed but still detected by other means.

### 2. Enhanced Browser Properties
```python
await page.evaluate('''() => {
    Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
    Object.defineProperty(navigator, 'plugins', { get: () => [
        { name: 'Chrome PDF Plugin' },
        { name: 'Chrome PDF Viewer' },
        { name: 'Native Client' }
    ]});
    
    window.chrome = {
        app: { isInstalled: false },
        runtime: {},
        loadTimes: function(){},
        csi: function(){},
        webstore: {}
    };
}''')
```
Result: Improved evasion but still detected.

### 3. WebGL Fingerprint Randomization
```python
await page.evaluate('''() => {
    const getParameter = WebGLRenderingContext.getParameter;
    WebGLRenderingContext.prototype.getParameter = function(parameter) {
        if (parameter === 37445) {
            return 'Intel Inc.';
        }
        if (parameter === 37446) {
            return 'Intel Iris OpenGL Engine';
        }
        return getParameter(parameter);
    };
}''')
```
Result: Better WebGL fingerprint but still detected.

## Current Challenges

1. **Popup Handling**: The main challenge is handling the Google login popup. Perplexity seems to detect automation when we try to:
   - Click the Google login button
   - Handle the popup window
   - Navigate to the Google login page

2. **Browser Detection**: Despite extensive evasion techniques, Perplexity still detects automation through:
   - Browser fingerprinting
   - Event validation
   - Behavioral analysis

3. **Frame Management**: Issues with frame detachment and navigation:
   ```
   Error: Page.goto: net::ERR_ABORTED; maybe frame was detached?
   ```

## Current Best Approach

The most successful approach combines:

1. Enhanced browser launch arguments
2. Realistic context configuration
3. Human-like interaction patterns
4. Comprehensive fingerprint evasion
5. Direct page navigation instead of popup handling

However, success rate remains inconsistent due to Perplexity's sophisticated anti-automation measures.

## Future Directions

1. Investigate using browser profiles to maintain login state
2. Explore alternative authentication flows
3. Implement more sophisticated behavioral patterns
4. Consider using authenticated API endpoints if available
5. Monitor for changes in Perplexity's anti-automation measures

## Error Patterns and Solutions

### Common Errors

1. **Timeout Waiting for Popup**
   ```
   TimeoutError: Timeout 30000ms exceeded while waiting for event "popup"
   ```
   Attempted Solutions:
   - Pre-create popup page
   - Use direct navigation
   - Implement click retry logic

2. **Frame Detachment**
   ```
   Error: Page.goto: net::ERR_ABORTED; maybe frame was detached?
   ```
   Attempted Solutions:
   - Wait for frame stability
   - Handle frame navigation events
   - Use main page context

3. **Button Click Failures**
   ```
   Error: Could not click Google login button
   ```
   Attempted Solutions:
   - Remove overlays
   - Force click via JavaScript
   - Simulate human-like interaction

## Logging and Debugging

Current logging implementation:
```python
logger = setup_logging(__name__)

# Example debug logs
logger.info("Starting login flow...")
logger.info("Found login button with selector: {selector}")
logger.error(f"Error during Google login: {str(e)}")
```

## Testing Methodology

1. **Manual Testing**
   - Compare automated vs manual interaction
   - Analyze network requests
   - Monitor browser fingerprint

2. **Automated Testing**
   - Retry logic with exponential backoff
   - Multiple browser configurations
   - Various user agent rotations

## Dependencies

Required packages:
```python
patchright==1.0.0  # Browser automation
asyncio  # Async operations
logging  # Debug logging
random  # Randomization for human-like behavior
time  # Timing and delays
``` 