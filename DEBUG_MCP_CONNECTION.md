# MCP Connection Debugging Guide

## Current Configuration Issue

Based on your logs and configuration, here's what we know:

### ✅ What's Working:
- **MCP Toolbox**: Running successfully, initialized 7 tools
- **LiveKit Agent**: Connected to LiveKit Cloud
- **Docker Network**: Services can communicate

### ❌ Potential Issues:

#### 1. **MCP Protocol Endpoint**
MCP Toolbox might not use `/health` endpoint. Try these URLs:
- `http://mcp-toolbox:5000` (root)
- `http://mcp-toolbox:5000/mcp` (MCP protocol endpoint)
- `http://mcp-toolbox:5000/api` (API endpoint)

#### 2. **Port Configuration Mismatch**
Current setup:
```yaml
mcp-toolbox:
  ports: "5001:5000"  # External:Internal
  environment:
    - TOOLBOX_PORT=5000
    - TOOLBOX_HOST=0.0.0.0

livekit-agent:
  environment:
    - TOOLBOX_URL=http://mcp-toolbox:5000  # Using internal port
```

## 🔍 Quick Tests to Run

### Test 1: Check MCP Toolbox Endpoints
From your Coolify terminal or another container:

```bash
# Test if MCP Toolbox is reachable
curl http://mcp-toolbox:5000
curl http://mcp-toolbox:5000/health
curl http://mcp-toolbox:5000/mcp
curl http://mcp-toolbox:5000/api
```

### Test 2: Check MCP Toolbox Logs
Look for these patterns in MCP Toolbox logs:
- What endpoints are being served?
- Any incoming connection attempts?
- Error messages about protocol or endpoints?

### Test 3: Test from LiveKit Agent Container
```bash
# From inside the livekit-agent container
curl http://mcp-toolbox:5000
ping mcp-toolbox
```

## 🎯 Most Likely Solutions

### Solution 1: Update TOOLBOX_URL
The MCP protocol might expect a specific endpoint:

```yaml
environment:
  - TOOLBOX_URL=http://mcp-toolbox:5000/mcp
```

### Solution 2: Check MCP Toolbox Documentation
MCP Toolbox might serve on a different path or require specific headers.

### Solution 3: Use External URL for Testing
Temporarily test with external URL:

```yaml
environment:
  - TOOLBOX_URL=http://your-coolify-domain:5001
```

## 🚨 Debug Steps

1. **Check current logs** for any connection attempts
2. **Test MCP endpoints** manually with curl
3. **Update TOOLBOX_URL** based on findings
4. **Redeploy** and test again
5. **Monitor logs** for tool call attempts

## 📋 Expected Log Patterns

### If Connection Works:
```
✅ MCP Toolbox connection test successful
📋 Available MCP tools: 7 tools found
🔧 Tool called: search-volunteers-by-skills
```

### If Connection Fails:
```
❌ MCP Toolbox connection test failed: [error details]
```

The enhanced logging in the agent will show exactly where the connection is failing.