# 🔐 Google Calendar Authentication in Coolify

## Current Status Analysis

Based on your deployment logs, the Google Calendar MCP server is running successfully but needs OAuth authentication. Here's how to complete the setup:

## 📋 Log Analysis

Your logs show:
```
✅ Google Calendar MCP Server listening on http://0.0.0.0:3000
⚠️  No valid normal user authentication tokens found.
❌ {"jsonrpc":"2.0","error":{"code":-32000,"message":"Not Acceptable: Client must accept text/event-stream"},"id":null}
```

**Status**: Server is running, but needs authentication and has a transport configuration issue.

## 🔧 Solution Steps

### Step 1: Complete OAuth Authentication

The server is waiting for you to authenticate. Here's how:

1. **Access the Google Calendar MCP container in Coolify:**
   - Go to your Coolify dashboard
   - Navigate to your project
   - Find the `google-calendar-mcp` service
   - Click on "Terminal" or "Exec"

2. **Run the authentication command:**
   ```bash
   npx @cocal/google-calendar-mcp auth
   ```

3. **Follow the authentication flow:**
   - The command will display a Google OAuth URL
   - Copy the URL and open it in your browser
   - Sign in with your Google account
   - Grant calendar permissions
   - The authentication tokens will be saved automatically

### Step 2: Verify Authentication

After completing OAuth:

1. **Check the container logs again:**
   - Look for "Authentication successful" messages
   - Verify no more "No valid tokens" warnings

2. **Test the health endpoint:**
   ```bash
   curl http://your-coolify-url:3000/health
   ```
   Should return: `{"status":"healthy","server":"google-calendar-mcp"}`

### Step 3: Restart Services (if needed)

If authentication doesn't take effect immediately:

1. **Restart the Google Calendar MCP service:**
   - In Coolify dashboard, restart the `google-calendar-mcp` service
   - Wait for it to come back online

2. **Restart the LiveKit agent:**
   - Restart the `livekit-agent` service to refresh MCP connections

## 🐛 Troubleshooting Common Issues

### Issue 1: "Client must accept text/event-stream"
**Cause**: HTTP transport configuration mismatch
**Solution**: The updated docker-compose.yaml should fix this. Redeploy if needed.

### Issue 2: Authentication URL not appearing
**Symptoms**: No OAuth URL in container logs
**Solutions**:
1. Ensure all Google environment variables are set in Coolify
2. Check that the OAuth credentials file was generated correctly
3. Verify Google Calendar API is enabled in Google Cloud Console

### Issue 3: Error 403: access_denied / "App not verified"
**Cause**: OAuth consent screen configuration issue
**Error Message**: "Voice_Agent has not completed the Google verification process"
**Solution**: See **[GOOGLE_OAUTH_CONSENT_FIX.md](GOOGLE_OAUTH_CONSENT_FIX.md)** for complete fix

**Quick Fix:**
1. Go to Google Cloud Console → OAuth consent screen
2. Add your email as a test user
3. Wait 5-10 minutes for propagation
4. Try authentication again

### Issue 4: "Invalid client" error during OAuth
**Cause**: Incorrect OAuth credentials
**Solutions**:
1. Verify `GOOGLE_CLIENT_ID` matches your Google Cloud Console credentials
2. Ensure `GOOGLE_CLIENT_SECRET` is correct
3. Check that `GOOGLE_PROJECT_ID` matches your Google Cloud project

### Issue 5: Tokens not persisting
**Cause**: Volume mounting issues
**Solution**: Ensure the `google-calendar-tokens` volume is properly mounted

## 🔍 Verification Commands

Run these in the Google Calendar MCP container to verify setup:

```bash
# Check if credentials file exists and is valid
cat /app/gcp-oauth.keys.json

# Check if tokens directory exists
ls -la /root/.config/google-calendar-mcp/

# Test authentication status
npx @cocal/google-calendar-mcp --help

# Manual authentication if needed
npx @cocal/google-calendar-mcp auth
```

## 📱 Testing End-to-End Integration

Once authentication is complete:

1. **Connect your React Native app** to the deployed voice agent
2. **Test calendar functionality:**
   - "I need help with cooking in Accra"
   - "Can you schedule an appointment with Sarah for tomorrow at 2 PM?"
3. **Verify calendar creation:**
   - Check your Google Calendar for the created appointment
   - Confirm all details are correct

## 🚀 Expected Successful Flow

After authentication, your logs should show:
```
✅ Google Calendar MCP Server listening on http://0.0.0.0:3000
✅ Authentication tokens loaded successfully
✅ Ready to handle calendar requests
```

And your voice agent should be able to:
- Search for volunteers
- Schedule appointments
- View existing appointments
- Modify/cancel appointments

## 🔄 Re-authentication (if needed)

If tokens expire or become invalid:

1. **Access the container terminal**
2. **Run re-authentication:**
   ```bash
   npx @cocal/google-calendar-mcp auth
   ```
3. **Complete the OAuth flow again**
4. **Restart the service**

## 📞 Next Steps

1. **Complete OAuth authentication** using the steps above
2. **Verify health endpoints** are responding correctly
3. **Test voice agent integration** with your React Native app
4. **Monitor logs** for any remaining issues

Your Google Calendar MCP integration is almost ready - just needs the OAuth authentication completed!