import os
import logging
from dotenv import load_dotenv

from livekit import agents
from livekit.plugins import openai
from livekit.plugins import deepgram
from livekit.agents import AgentSession, Agent, RoomInputOptions, mcp
from livekit.plugins import noise_cancellation, silero

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("volunteer-agent")

# Create MCP logger for debugging tool calls
mcp_logger = logging.getLogger("mcp-tools")
mcp_logger.setLevel(logging.DEBUG)


def _ensure_database_path():
    """Ensure the tools.yaml file points to the correct database path."""
    import os

    # Get the absolute path to the volunteer database
    project_root = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(project_root, "volunteers.db")

    # Path to the YAML file
    yaml_path = os.path.join(project_root, "tools.yaml")

    try:
        with open(yaml_path, 'r') as f:
            yaml_content = f.read()

        # Check if the database path needs updating
        if db_path.replace('\\', '/') not in yaml_content:
            # Update the database path in YAML content
            lines = yaml_content.split('\n')
            for i, line in enumerate(lines):
                if 'database:' in line and 'volunteers-db' in yaml_content[:yaml_content.find(line)]:
                    # Update the database path with forward slashes for cross-platform compatibility
                    lines[i] = f'    database: "{db_path.replace(chr(92), "/")}"'
                    break

            # Write back the updated content
            with open(yaml_path, 'w') as f:
                f.write('\n'.join(lines))

            logger.info(f"Updated database path in YAML to: {db_path}")
        else:
            logger.info("Database path already correct in YAML")

    except Exception as e:
        logger.warning(f"Could not update YAML database path: {e}")


class VolunteerAssistant(Agent):
    """AI Assistant for Elderly People to Find Volunteers"""
    
    def __init__(self):
        super().__init__(
            instructions="""You are a caring and patient voice AI assistant helping elderly people in Ghana find volunteers to assist them with their daily needs.
            
            You speak to elderly users with respect, warmth, and patience. You understand they may need extra time and clear explanations.
            
            **IMPORTANT: You MUST use the available MCP tools to search for volunteers. Always call the appropriate tool when a user asks for help.**
            
            **Available Tools to Help Find Volunteers:**
            - search-volunteers-by-skills: Find volunteers who can help with specific tasks (cooking, companionship, transportation, medication reminders, light housekeeping, etc.)
            - search-volunteers-by-location: Find volunteers near you (Accra, Kumasi, Tamale, Cape Coast, Tema, etc.)
            - get-available-volunteers: Show volunteers who are free to help right now
            - get-volunteers-by-transport: Find volunteers who have cars or can use public transport to reach you
            - get-experienced-volunteers: Find volunteers with many years of experience helping elderly people
            - search-volunteers-by-language: Find volunteers who speak your preferred language (English, Twi, Ga, Hausa, etc.)
            - get-volunteer-by-id: Get more details about a specific volunteer
            
            **Your Communication Style:**
            - Speak slowly, clearly, and patiently
            - Use simple, everyday language (avoid technical terms)
            - Be very warm, respectful, and encouraging
            - Show genuine care and concern for their wellbeing
            - Repeat important information if needed
            - Be culturally respectful and appropriate for Ghanaian elderly
            
            **When sharing volunteer information:**
            - Always mention the volunteer's name and where they live
            - Explain what kind of help they can provide
            - Tell them if the volunteer is available now
            - Mention how many years of experience they have
            - Share what languages they speak
            - Explain how they can travel to help (car, public transport, etc.)
            - Include their phone number so they can contact them
            
            **Common needs you help with:**
            - Finding someone to cook meals or help with cooking
            - Finding a companion to talk with and spend time
            - Finding help with transportation to doctor visits or shopping
            - Finding someone to remind about medications
            - Finding help with light housekeeping or cleaning
            - Finding someone who speaks their local language
            
            **Your approach:**
            1. Listen carefully to what kind of help they need
            2. Ask gentle questions to understand their location and preferences
            3. **ALWAYS use the MCP tools to search the volunteer database**
            4. Present 2-3 good volunteer options clearly and simply
            5. Offer to find more volunteers if they want different options
            6. Be encouraging and reassuring throughout
            
            **CRITICAL: When a user asks for help finding volunteers, you MUST call one of the MCP tools. Do not provide generic responses without searching the database first.**
            
            Remember: You are helping elderly people find caring volunteers to assist them. Be patient, kind, and thorough in your help.""",
        )
    
    async def on_tool_call(self, tool_call):
        """Log all tool calls for debugging"""
        mcp_logger.info(f"🔧 Tool called: {tool_call.name}")
        mcp_logger.info(f"📝 Tool arguments: {tool_call.arguments}")
        
        try:
            result = await super().on_tool_call(tool_call)
            mcp_logger.info(f"✅ Tool result: {result}")
            return result
        except Exception as e:
            mcp_logger.error(f"❌ Tool call failed: {e}")
            raise


async def entrypoint(ctx: agents.JobContext):
    """Main entrypoint for the LiveKit agent"""
    
    logger.info("Starting LiveKit Voice Agent for Volunteer Management")
    
    try:
        # Ensure database path is correct
        _ensure_database_path()
        
        # Validate required environment variables
        required_env_vars = [
            "AZURE_DEPLOYMENT",
            "AZURE_OPENAI_ENDPOINT",
            "AZURE_OPENAI_API_KEY",
            "OPENAI_API_VERSION",
            "DEEPGRAM_API_KEY",
            "AZURE_TTS_DEPLOYMENT",
            "AZURE_TTS_ENDPOINT",
            "AZURE_TTS_API_KEY",
            "AZURE_TTS_API_VERSION"
        ]
        
        missing_vars = [var for var in required_env_vars if not os.getenv(var)]
        if missing_vars:
            logger.error(f"Missing required environment variables: {missing_vars}")
            raise ValueError(f"Missing environment variables: {missing_vars}")

        # Get MCP Toolbox URL from environment or use default for Docker Compose
        toolbox_url = os.getenv("TOOLBOX_URL", "http://mcp-toolbox:5000/mcp")
        logger.info(f"Connecting to MCP Toolbox at: {toolbox_url}")

        # Test MCP connection before creating session
        try:
            import aiohttp
            async with aiohttp.ClientSession() as http_session:
                async with http_session.get(f"{toolbox_url}/health") as response:
                    if response.status == 200:
                        logger.info("✅ MCP Toolbox connection test successful")
                    else:
                        logger.warning(f"⚠️ MCP Toolbox health check returned status: {response.status}")
        except Exception as e:
            logger.error(f"❌ MCP Toolbox connection test failed: {e}")

        # Create MCP server with detailed logging
        mcp_server = mcp.MCPServerHTTP(toolbox_url)
        logger.info(f"✅ Created MCP server instance for: {toolbox_url}")

        session = AgentSession(
            llm=openai.LLM.with_azure(
                azure_deployment=os.getenv("AZURE_DEPLOYMENT"),
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                api_version=os.getenv("OPENAI_API_VERSION"),
            ),
            stt=deepgram.STT(
                model="nova-3",
                api_key=os.getenv("DEEPGRAM_API_KEY")
            ),
            tts=openai.TTS.with_azure(
                model=os.getenv("AZURE_TTS_DEPLOYMENT"),
                voice="coral",
                azure_endpoint=os.getenv("AZURE_TTS_ENDPOINT"),
                azure_deployment=os.getenv("AZURE_TTS_DEPLOYMENT"),
                api_key=os.getenv("AZURE_TTS_API_KEY"),
                api_version=os.getenv("AZURE_TTS_API_VERSION"),
            ),
            vad=silero.VAD.load(),
            # Use LiveKit's native MCP support
            mcp_servers=[mcp_server]
        )

        logger.info("✅ Agent session configured successfully with MCP integration")

        # Create agent with enhanced logging
        agent = VolunteerAssistant()
        logger.info("✅ VolunteerAssistant agent created")

        await session.start(
            room=ctx.room,
            agent=agent,
            room_input_options=RoomInputOptions(
                noise_cancellation=noise_cancellation.BVC(),
            ),
        )

        logger.info("✅ Agent session started successfully")

        # Log available MCP tools
        try:
            # Get tools from MCP server
            tools_info = await mcp_server.list_tools()
            logger.info(f"📋 Available MCP tools: {len(tools_info)} tools found")
            for tool in tools_info:
                logger.info(f"  🔧 Tool: {tool.name} - {tool.description}")
        except Exception as e:
            logger.error(f"❌ Failed to list MCP tools: {e}")

        await session.generate_reply(
            instructions="""Greet the elderly user very warmly and introduce yourself as a caring AI assistant who helps elderly people in Ghana find volunteers.
            Speak slowly and clearly. Explain that you are here to help them find kind volunteers who can assist with daily needs like cooking,
            companionship, transportation to appointments, medication reminders, light housekeeping, and other helpful tasks.
            Mention that you can find volunteers near their location who speak their preferred language.
            Ask gently what kind of help they are looking for today, and reassure them that you will take your time to find the right volunteer for them."""
        )

        logger.info("✅ Initial greeting generated successfully")

    except Exception as e:
        logger.error(f"❌ Error in agent entrypoint: {e}")
        raise


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))