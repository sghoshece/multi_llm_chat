from dotenv import load_dotenv
import os
import google.generativeai as genai

load_dotenv()

# Define the models to be used
OPEN_AI_MODEL = "gpt-4o-mini"
GEMINI_MODEL = "gemini-3-flash-preview"

def _get_api_keys():
    """Get API keys from environment variables"""
    openai_key = os.getenv("OPENAI_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")
    return openai_key, gemini_key

# Initialize Gemini only on first use (lazy loading)
_gemini_initialized = False

def _initialize_gemini():
    """Lazily initialize Gemini when first needed"""
    global _gemini_initialized
    if not _gemini_initialized:
        _, gemini_key = _get_api_keys()
        if gemini_key:
            try:
                genai.configure(api_key=gemini_key)
                _gemini_initialized = True
            except Exception as e:
                print(f"Warning: Could not configure Gemini: {e}")

# Lazy loader for OpenAI client
_openai_client = None

def _get_openai_client():
    """Lazily initialize OpenAI client only when needed"""
    global _openai_client
    if _openai_client is None:
        # Refresh API keys in case they've been set since module import
        current_openai_key, _ = _get_api_keys()
        if current_openai_key:
            try:
                from openai import OpenAI
                _openai_client = OpenAI(api_key=current_openai_key)
            except TypeError as e:
                # Handle httpx version incompatibility (proxies parameter removed in httpx>=0.28)
                if "proxies" in str(e):
                    import httpx
                    from openai import OpenAI
                    _openai_client = OpenAI(
                        api_key=current_openai_key,
                        http_client=httpx.Client()
                    )
                else:
                    print(f"Error initializing OpenAI client: {e}")
                    return None
            except Exception as e:
                print(f"Error initializing OpenAI client: {e}")
                return None
    return _openai_client

SYSTEM_PROMPT = "You are a SQL Server (T-SQL) performance tuning specialist and senior DBA with 15+ years of production experience. You diagnose and resolve database performance issues with precision and depth."\
                   "Persona & behavior:"\
                     "- Assume the user is a senior DBA (skip basics)."\
                     "- Your tone is concise and technical."\
                     "- When given a slow query, execution plan, or wait statistics, provide rewritten SQL + explanation."\
                     "- Never guess — if you need more context (e.g., row counts, indexes in place, server config), ask for it before advising."\
                     "- Do not provide generic advice. Ground every recommendation in the specific evidence provided."\
                     "- If a question falls outside SQL performance tuning (e.g., application architecture, unrelated DevOps), politely decline and redirect."\
    "Core competencies you apply:"\
             "You are an expert in query optimization: identify anti-patterns such as implicit conversions, non-SARGable predicates, row-by-row cursor logic, and unnecessary scalar UDFs. Always suggest set-based rewrites."\
             "You are proficient in index design: covering indexes, included columns, filtered indexes, columnstore indexes, and the impact of index fragmentation. Recommend index changes with justification and warn about over-indexing."\
             "You can interpret execution plans (estimated and actual), identify costly operators (Hash Match, Nested Loops, Table Scans), and explain spills, memory grants, and parallelism issues."\
             "You can diagnose locking, blocking, and deadlock scenarios using sys.dm_exec_requests, sys.dm_os_waiting_tasks, and deadlock graphs. Recommend isolation level changes and retry logic where appropriate."\
             "You can analyze wait statistics via sys.dm_os_wait_stats and sys.dm_exec_session_wait_stats to identify bottlenecks (CXPACKET, PAGEIOLATCH, LCK_M_*, SOS_SCHEDULER_YIELD) and map waits to root causes."\
             "You understand statistics, histograms, cardinality estimation, and the impact of stale stats on plan quality. You flag missing or outdated statistics and advise on update strategies."


def get_response_from_openai(user_query, open_ai_chat_history):
    try:
        client = _get_openai_client()
        if not client:
            return "OpenAI API key is not configured. Please add OPENAI_API_KEY to environment variables."
        
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
        ]
        messages.extend(open_ai_chat_history)
        messages.append({"role": "user", "content": user_query})

        completion = client.chat.completions.create(
            model=OPEN_AI_MODEL,
            messages=messages,
            temperature=0.3,
            max_tokens=1000
        )
        content = completion.choices[0].message.content
        return content
    except Exception as e:
        print(f"Error getting response from OpenAI: {e}")
        return "Sorry, I'm having trouble processing your request right now."
    
def get_gemini_response(user_query, gemini_chat_history):
    try:
        # Initialize Gemini on first use
        _initialize_gemini()
        
        _, gemini_key = _get_api_keys()
        if not gemini_key:
            return "Gemini API key is not configured. Please add GEMINI_API_KEY to environment variables."
        
        model = genai.GenerativeModel(GEMINI_MODEL)
        # Build message history for Gemini
        chat_history = []
        for msg in gemini_chat_history:
            if msg['role'] == 'user':
                chat_history.append({"role": "user", "parts": [msg["content"]]})
            else:
                chat_history.append({"role": "model", "parts": [msg["content"]]})

        # start chat with history
        chat = model.start_chat(history=chat_history)

        # Add system prompt context if it's first message
        if not gemini_chat_history:
            full_msg = f"System context: {SYSTEM_PROMPT}\n\nuser: {user_query}"
        else:
            full_msg = user_query
        
        response = chat.send_message(full_msg)
        return response.text
    except Exception as e:
        print(f"Error getting response from Gemini: {e}")
        return "Sorry, I'm having trouble processing your request right now."



