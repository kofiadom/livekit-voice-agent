import os
import logging
from dotenv import load_dotenv

from livekit import agents
from livekit.plugins import openai
from livekit.plugins import deepgram
from livekit.agents import AgentSession, Agent, RoomInputOptions, mcp
from livekit.plugins import noise_cancellation, silero

# Import our custom Google Calendar tools
from google_calendar_tools import (
    list_calendars,
    create_event,
    list_events,
    search_events,
    update_event,
    delete_event,
    get_freebusy
)

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
            # Add our custom Google Calendar tools to the agent
            tools=[
                list_calendars,
                create_event,
                list_events,
                search_events,
                update_event,
                delete_event,
                get_freebusy
            ],
            instructions="""You are a caring and patient voice AI assistant helping elderly people in Ghana find volunteers to assist them with their daily needs and schedule appointments with them.
            
            You speak to elderly users with respect, warmth, and patience. You understand they may need extra time and clear explanations.
            
            **IMPORTANT: You MUST use the available MCP tools to search for volunteers and manage calendar appointments. Always call the appropriate tool when a user asks for help.**
            
            **Available Tools to Help Find Volunteers:**
            - search-volunteers-by-skills: Find volunteers who can help with specific tasks (cooking, companionship, transportation, medication reminders, light housekeeping, etc.)
            - search-volunteers-by-location: Find volunteers near you (Accra, Kumasi, Tamale, Cape Coast, Tema, etc.)
            - get-available-volunteers: Show volunteers who are free to help right now
            - get-volunteers-by-transport: Find volunteers who have cars or can use public transport to reach you
            - get-experienced-volunteers: Find volunteers with many years of experience helping elderly people
            - search-volunteers-by-language: Find volunteers who speak your preferred language (English, Twi, Ga, Hausa, etc.)
            - get-volunteer-by-id: Get more details about a specific volunteer
            
            **Available Calendar Tools for Scheduling:**
            - list-calendars: Show available calendars for scheduling
            - create-event: Schedule appointments with volunteers (include volunteer name, service type, date, time, location)
            - list-events: Show upcoming appointments
            - search-events: Find specific appointments
            - update-event: Change appointment details
            - delete-event: Cancel appointments
            - get-freebusy: Check when you and volunteers are available
            
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
            - **OFFER TO SCHEDULE AN APPOINTMENT** with the volunteer
            
            **When scheduling appointments:**
            - Ask for preferred date and time in a gentle way
            - Confirm the type of help needed (cooking, companionship, etc.)
            - Include the volunteer's name and contact information in the appointment
            - Set the location (usually the elderly person's home)
            - Create clear appointment titles like "Cooking Help with Sarah Johnson"
            - Always confirm the appointment details before creating it
            
            **Common needs you help with:**
            - Finding someone to cook meals or help with cooking
            - Finding a companion to talk with and spend time
            - Finding help with transportation to doctor visits or shopping
            - Finding someone to remind about medications
            - Finding help with light housekeeping or cleaning
            - Finding someone who speaks their local language
            - **Scheduling regular or one-time appointments with volunteers**
            
            **Your enhanced approach:**
            1. Listen carefully to what kind of help they need
            2. Ask gentle questions to understand their location and preferences
            3. **ALWAYS use the MCP tools to search the volunteer database**
            4. Present 2-3 good volunteer options clearly and simply
            5. **ASK IF THEY WANT TO SCHEDULE AN APPOINTMENT** with any volunteer
            6. If they want to schedule, use calendar tools to create the appointment
            7. Confirm all appointment details and provide a summary
            8. Offer to find more volunteers or schedule additional appointments if needed
            9. Be encouraging and reassuring throughout
            
            **CRITICAL: When a user asks for help finding volunteers, you MUST call the volunteer search MCP tools. When they want to schedule appointments, you MUST use the calendar MCP tools. Do not provide generic responses without using the appropriate tools first.**
            
            Remember: You are helping elderly people find caring volunteers AND schedule appointments with them. Be patient, kind, and thorough in your help. Always offer to schedule appointments after finding suitable volunteers.""",
        )
    
    async def on_tool_call(self, tool_call):
        """Log all tool calls for debugging with enhanced emojis"""
        mcp_logger.info(f"🚀 ===== MCP TOOL CALL START =====")
        mcp_logger.info(f"🔧 Tool Name: {tool_call.name}")
        mcp_logger.info(f"📝 Arguments: {tool_call.arguments}")
        mcp_logger.info(f"🆔 Call ID: {getattr(tool_call, 'id', 'N/A')}")
        
        try:
            result = await super().on_tool_call(tool_call)
            mcp_logger.info(f"✅ SUCCESS: Tool executed successfully")
            mcp_logger.info(f"📊 Result Preview: {str(result)[:200]}{'...' if len(str(result)) > 200 else ''}")
            mcp_logger.info(f"🏁 ===== MCP TOOL CALL END =====")
            return result
        except Exception as e:
            mcp_logger.error(f"❌ FAILED: Tool call failed with error: {e}")
            mcp_logger.error(f"🏁 ===== MCP TOOL CALL END (ERROR) =====")
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

        # Get MCP server URLs from environment
        toolbox_url = os.getenv("TOOLBOX_URL", "http://mcp-toolbox:5000/mcp")
        
        logger.info(f"Connecting to MCP Toolbox at: {toolbox_url}")
        logger.info("Using custom Google Calendar tools (no MCP server needed)")

        # Test MCP connections before creating session
        import aiohttp
        
        # Test Toolbox connection
        try:
            async with aiohttp.ClientSession() as http_session:
                async with http_session.get(f"{toolbox_url}/health") as response:
                    if response.status == 200:
                        logger.info("✅ MCP Toolbox connection test successful")
                    else:
                        logger.warning(f"⚠️ MCP Toolbox health check returned status: {response.status}")
        except Exception as e:
            logger.error(f"❌ MCP Toolbox connection test failed: {e}")

        # Create MCP servers with detailed logging
        mcp_toolbox_server = mcp.MCPServerHTTP(toolbox_url)
        
        logger.info(f"✅ Created MCP Toolbox server instance for: {toolbox_url}")

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
            # Use LiveKit's native MCP support with toolbox server only
            # Google Calendar tools are now integrated directly into the agent
            mcp_servers=[mcp_toolbox_server]
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

        # Log available tools from MCP server and custom tools
        total_tools = 0
        
        # List tools from MCP Toolbox
        try:
            toolbox_tools = await mcp_toolbox_server.list_tools()
            logger.info(f"📋 MCP Toolbox tools: {len(toolbox_tools)} tools found")
            total_tools += len(toolbox_tools)
            for tool in toolbox_tools:
                # Handle different tool object types
                if hasattr(tool, 'name'):
                    logger.info(f"  🔧 Volunteer Tool: {tool.name} - {getattr(tool, 'description', 'No description')}")
                elif hasattr(tool, '__name__'):
                    logger.info(f"  🔧 Volunteer Tool: {tool.__name__} - Function tool")
                else:
                    logger.info(f"  🔧 Volunteer Tool: {str(tool)} - Unknown tool type")
        except Exception as e:
            logger.error(f"❌ Failed to list MCP Toolbox tools: {e}")
        
        # List custom Google Calendar tools
        calendar_tools = [
            list_calendars,
            create_event,
            list_events,
            search_events,
            update_event,
            delete_event,
            get_freebusy
        ]
        logger.info(f"📅 Custom Google Calendar tools: {len(calendar_tools)} tools found")
        total_tools += len(calendar_tools)
        for tool in calendar_tools:
            tool_name = getattr(tool, '__name__', str(tool))
            logger.info(f"  📅 Calendar Tool: {tool_name} - Custom LiveKit function tool")
        
        logger.info(f"🎯 Total tools available: {total_tools} (MCP + Custom)")

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