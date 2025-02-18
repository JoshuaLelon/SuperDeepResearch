**Summary of Problem**  
You need a research function that headlessly navigates Gemini (the proprietary Google AI tool) without relying on external dependencies like Selenium or “relishplus”. Instead, the function should leverage NoDriver to programmatically open pages, sign in, configure research mode, execute queries, and extract results, all while maintaining robust error handling and concurrency.

**Summary of Solution**  
Use NoDriver’s asynchronous approach to launch a headless Chromium-like browser. Programmatically log into Gemini, switch to the right research mode, submit queries, and parse results. This mirrors how `gemini.py` flow is structured (login, research setup, query, extraction), but replaced with NoDriver’s architecture.

NoDriver docs: https://ultrafunkamsterdam.github.io/nodriver/

Below is a step-by-step plan:

---

### Implementation Plan

- [ ] **Pick or Create a New Function**  
  - Define a function named `async def gemini_deep_research_nodriver(plan: str) -> str:` or similar.  
  - Store it in the same file (`single_research.py`) or a new file if you prefer a separate module.

- [ ] **Set Up Environment and Imports**  
  - Import the NoDriver module:  
    ```python
    import nodriver as uc
    ```  
  - Optionally import additional pieces you need from NoDriver (e.g., config, exceptions).
  - Ensure any logging or environment config occurs properly (mirroring your `single_research.py` approach).

- [ ] **Configure the NoDriver Browser**  
  - Use NoDriver’s `Config` or direct method calls to specify:  
    - `headless=True`  
    - Possibly `user_data_dir` if you need persistent sessions  
    - Possibly `browser_args` like `['--disable-web-security', '--disable-gpu']` if needed  
  - Example:
    ```python
    config = uc.Config()
    config.headless = True
    # add more config if needed...
    ```

- [ ] **Launch Browser Session**  
  - Asynchronously start the browser:  
    ```python
    driver = await uc.start(config)
    ```
  - This returns a `browser` or `driver` object representing the active session.

- [ ] **Implement Login Flow**  
  1. **Navigate to Gemini**:  
     ```python
     tab = await driver.get("https://gemini.google.com/app")
     ```
  2. **Check if a “Sign in” button is present**:  
     ```python
     sign_in_button = await tab.find("Sign in", best_match=True)
     if sign_in_button:
         await sign_in_button.click()
     ```
  3. **Fill in credentials**:  
     - **Handle email**:  
       ```python
       email_elem = await tab.select("input[type=email]")
       await email_elem.send_keys("your_email")
       ```
     - **Handle password**:  
       ```python
       pwd_elem = await tab.select("input[type=password]")
       await pwd_elem.send_keys("your_password")
       ```
     - **Submit**:  
       ```python
       next_button = await tab.find("next", best_match=True)
       await next_button.click()
       ```
  4. **(Optional) Two-Factor**:  
     - If you need to handle 2FA, let NoDriver wait for relevant UI elements.

- [ ] **Set Up Research Mode**  
  1. **Locate “model selector dropdown”** typically a clickable element with text “Gemini 1.5 Pro with Deep Research”.  
  2. **Wait for load** using `await tab.sleep(1)` or a more targeted “wait for element.”  
  3. **Select that model** (perhaps a dropdown or list item).  
  4. **Click “Try Now”** if prompted.

- [ ] **Submit Your Plan as a Query**  
  - Something like:
    ```python
    query_elem = await tab.select("textarea, input")
    await query_elem.send_keys(plan)
    await query_elem.send_keys("\n")  # or click a send button
    ```
  - Wait for it to process. Possibly do `await tab.sleep(2)` or wait for result elements.

- [ ] **Extract Results**  
  1. **Check the relevant paragraph or “final response” container**.  
  2. **Retrieve text** using NoDriver’s `Element` methods:
     ```python
     results_element = await tab.find("the main research findings", best_match=True)
     extracted_text = await results_element.text()
     return extracted_text
     ```
  3. **Handle edge cases** (like no result found).

- [ ] **Tidy Up**  
  - Close the browser with `await driver.stop()` in a `finally:` block to ensure no session leaks.  
  - Return the results as a string.

- [ ] **Update Documentation**  
  - Add a short explanation of the new function in `mcp_server/tools/README.md`.  
  - Update the parent or root `README.md` to reflect that you now have a new NoDriver-based Gemini research approach (plus any needed usage instructions).

---

That’s it! Once you follow and implement these steps, you’ll have a fully working NoDriver-based Gemini research function, closely imitating the overall flow from `gemini.py`. Have fun coding!
