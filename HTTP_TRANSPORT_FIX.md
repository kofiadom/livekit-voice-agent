# 🔧 HTTP Transport Issue Fix

## Problem Analysis

You're getting this error:
```
{"jsonrpc":"2.0","error":{"code":-32000,"message":"Not Acceptable: Client must accept text/event-stream"},"id":null}
```

**Root Cause**: The Google Calendar MCP server is running in Server-Sent Events (SSE) mode, but the LiveKit agent expects standard HTTP JSON-RPC communication.

## ✅ Solution Applied

The updated `docker-compose.yaml` now properly configures the Google Calendar MCP server for HTTP transport compatibility with LiveKit.

### Key Changes Made:

1. **Environment Variables**: Set `TRANSPORT=http`, `HOST=0.0.0.0`, `PORT=3000` as environment variables
2. **Command Simplification**: Removed conflicting transport flags from the command line
3. **Better Logging**: Added clearer startup messages for debugging

## 🚀 Deployment Steps

### Step 1: Redeploy with Fixed Configuration

```bash
git add docker-compose.yaml HTTP_TRANSPORT_FIX.md
git commit -m "Fix Google Calendar MCP HTTP transport compatibility"
git push origin main
```

Then redeploy in Coolify.

### Step 2: Verify the Fix

After redeployment, check the Google Calendar MCP logs in Coolify:

**Expected Success Logs:**
```
✅ Creating OAuth credentials file...
✅ Installing Google Calendar MCP...
✅ Starting Google Calendar MCP Server...
✅ OAuth credentials file created at /app/gcp-oauth.keys.json
✅ Server starting in HTTP transport mode for LiveKit compatibility
✅ Available at http://0.0.0.0:3000
✅ Google Calendar MCP Server listening on http://0.0.0.0:3000
```

**No More Error:**
- ❌ `{"jsonrpc":"2.0","error":{"code":-32000,"message":"Not Acceptable: Client must accept text/event-stream"},"id":null}`

### Step 3: Complete Authentication (After Transport Fix)

Once the transport issue is resolved and you've waited 10 minutes for OAuth test user propagation:

1. **Access container terminal** in Coolify
2. **Run authentication**:
   ```bash
   npx @cocal/google-calendar-mcp auth
   ```
3. **Complete OAuth flow** in browser
4. **Restart services** if needed

## 🔍 Verification Commands

### Check HTTP Transport Mode
```bash
# In the google-calendar-mcp container
echo $TRANSPORT  # Should show: http
echo $HOST       # Should show: 0.0.0.0
echo $PORT       # Should show: 3000
```

### Test Health Endpoint
```bash
curl http://your-coolify-url:3000/health
# Should return: {"status":"healthy","server":"google-calendar-mcp"}
```

### Test MCP Connection from Agent
Check the LiveKit agent logs for:
```
✅ Google Calendar MCP connection test successful
✅ Google Calendar MCP tools: X tools found
```

## 🐛 Troubleshooting

### Still Getting Transport Error?
1. **Verify environment variables** are set correctly in Coolify
2. **Check container logs** for startup messages
3. **Restart both services**: google-calendar-mcp and livekit-agent
4. **Wait for full startup** before testing

### Authentication Still Failing?
1. **Ensure OAuth test user** has propagated (wait 10+ minutes)
2. **Try authentication** only after transport issue is resolved
3. **Check Google Cloud Console** OAuth consent screen settings

### Agent Can't Connect to Calendar MCP?
1. **Verify internal networking** between containers
2. **Check GOOGLE_CALENDAR_URL** environment variable in agent
3. **Ensure both services** are in the same Docker network

## 📋 Expected Success Flow

1. **Transport Fixed**: No more "text/event-stream" errors
2. **Authentication Completed**: OAuth tokens saved successfully
3. **Agent Connection**: LiveKit agent connects to Google Calendar MCP
4. **Tools Available**: Calendar tools appear in agent logs
5. **End-to-End Working**: Voice commands create calendar appointments

## 🎯 Next Steps

1. **Redeploy** with the fixed docker-compose.yaml
2. **Wait for services** to start up completely
3. **Verify transport** is working (no more SSE errors)
4. **Complete authentication** after transport is fixed
5. **Test calendar functionality** with voice commands

The HTTP transport issue should now be resolved with the updated configuration!