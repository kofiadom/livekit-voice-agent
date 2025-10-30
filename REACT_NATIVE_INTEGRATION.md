# React Native Integration Guide

This guide explains how to connect your React Native app to the FastAPI backend that exposes your Postgres database.

## Overview

Your architecture now looks like this:

```
React Native App → FastAPI (volunteer-api:8002) → Postgres Database (Coolify)
```

The FastAPI service acts as a secure intermediary between your mobile app and database.

**Note**: The API runs on port 8002 (mapped from internal port 8000) to avoid conflicts with other services on Coolify.

## API Endpoints

Once deployed on Coolify, your API will be available at: `https://your-app.coolify.domain`

### Available Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/health` | GET | Health check |
| `/api/volunteers` | GET | Get all volunteers (with filters) |
| `/api/volunteers/{id}` | GET | Get specific volunteer |
| `/api/volunteers/search/by-skill/{skill}` | GET | Search by skill |
| `/api/volunteers/search/by-location/{location}` | GET | Search by location |
| `/api/volunteers/available` | GET | Get available volunteers |

### Query Parameters for `/api/volunteers`

- `skill` - Filter by skill (e.g., "cooking", "companionship")
- `location` - Filter by location (e.g., "Boston", "New York")
- `available` - Filter by availability (true/false)
- `language` - Filter by language (e.g., "English", "Spanish")
- `limit` - Maximum results (default: 100)

## React Native Implementation

### Step 1: Install Dependencies

```bash
npm install axios
# or
yarn add axios
```

### Step 2: Create API Service

Create `services/volunteerApi.js`:

```javascript
import axios from 'axios';

// Replace with your actual Coolify URL after deployment
const API_URL = __DEV__
  ? 'http://localhost:8002'  // For local testing (port 8002)
  : 'https://your-app.coolify.domain';  // Production URL from Coolify

const api = axios.create({
  baseURL: API_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const volunteerApi = {
  // Get all volunteers with optional filters
  getVolunteers: async (filters = {}) => {
    try {
      const response = await api.get('/api/volunteers', { params: filters });
      return response.data;
    } catch (error) {
      console.error('Error fetching volunteers:', error);
      throw error;
    }
  },

  // Get specific volunteer by ID
  getVolunteer: async (id) => {
    try {
      const response = await api.get(`/api/volunteers/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching volunteer ${id}:`, error);
      throw error;
    }
  },

  // Search by skill
  searchBySkill: async (skill, limit = 50) => {
    try {
      const response = await api.get(`/api/volunteers/search/by-skill/${skill}`, {
        params: { limit }
      });
      return response.data;
    } catch (error) {
      console.error(`Error searching by skill ${skill}:`, error);
      throw error;
    }
  },

  // Search by location
  searchByLocation: async (location, limit = 50) => {
    try {
      const response = await api.get(`/api/volunteers/search/by-location/${location}`, {
        params: { limit }
      });
      return response.data;
    } catch (error) {
      console.error(`Error searching by location ${location}:`, error);
      throw error;
    }
  },

  // Get available volunteers
  getAvailableVolunteers: async (limit = 50) => {
    try {
      const response = await api.get('/api/volunteers/available', {
        params: { limit }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching available volunteers:', error);
      throw error;
    }
  },

  // Health check
  checkHealth: async () => {
    try {
      const response = await api.get('/health');
      return response.data;
    } catch (error) {
      console.error('Health check failed:', error);
      throw error;
    }
  },
};

export default volunteerApi;
```

### Step 3: Create a Volunteers Screen

Create `screens/VolunteersScreen.js`:

```javascript
import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  FlatList,
  ActivityIndicator,
  StyleSheet,
  TouchableOpacity,
  RefreshControl,
  TextInput,
} from 'react-native';
import { volunteerApi } from '../services/volunteerApi';

const VolunteersScreen = () => {
  const [volunteers, setVolunteers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);
  const [searchSkill, setSearchSkill] = useState('');

  useEffect(() => {
    loadVolunteers();
  }, []);

  const loadVolunteers = async (filters = {}) => {
    try {
      setLoading(true);
      setError(null);
      const data = await volunteerApi.getVolunteers(filters);
      setVolunteers(data.volunteers);
    } catch (err) {
      setError('Failed to load volunteers. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadVolunteers();
    setRefreshing(false);
  };

  const handleSearch = () => {
    if (searchSkill.trim()) {
      loadVolunteers({ skill: searchSkill });
    } else {
      loadVolunteers();
    }
  };

  const renderVolunteer = ({ item }) => (
    <TouchableOpacity 
      style={styles.volunteerCard}
      onPress={() => {/* Navigate to detail screen */}}
    >
      <Text style={styles.name}>{item.name}</Text>
      <Text style={styles.location}>📍 {item.location}</Text>
      <Text style={styles.skills}>🛠️ {item.skills}</Text>
      <Text style={styles.languages}>🗣️ {item.languages}</Text>
      <Text style={styles.experience}>
        ⭐ {item.years_experience} years experience
      </Text>
      <View style={styles.statusContainer}>
        <Text style={[
          styles.status,
          item.available ? styles.available : styles.unavailable
        ]}>
          {item.available ? '✅ Available' : '⏸️ Unavailable'}
        </Text>
      </View>
      {item.phone && (
        <Text style={styles.phone}>📞 {item.phone}</Text>
      )}
    </TouchableOpacity>
  );

  if (loading && !refreshing) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#007AFF" />
        <Text style={styles.loadingText}>Loading volunteers...</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.centerContainer}>
        <Text style={styles.errorText}>{error}</Text>
        <TouchableOpacity style={styles.retryButton} onPress={loadVolunteers}>
          <Text style={styles.retryButtonText}>Retry</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.searchContainer}>
        <TextInput
          style={styles.searchInput}
          placeholder="Search by skill (e.g., cooking)"
          value={searchSkill}
          onChangeText={setSearchSkill}
          onSubmitEditing={handleSearch}
        />
        <TouchableOpacity style={styles.searchButton} onPress={handleSearch}>
          <Text style={styles.searchButtonText}>Search</Text>
        </TouchableOpacity>
      </View>

      <FlatList
        data={volunteers}
        keyExtractor={(item) => item.id.toString()}
        renderItem={renderVolunteer}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Text style={styles.emptyText}>No volunteers found</Text>
          </View>
        }
        contentContainerStyle={styles.listContent}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  searchContainer: {
    flexDirection: 'row',
    padding: 10,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  searchInput: {
    flex: 1,
    height: 40,
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    paddingHorizontal: 12,
    marginRight: 10,
  },
  searchButton: {
    backgroundColor: '#007AFF',
    paddingHorizontal: 20,
    borderRadius: 8,
    justifyContent: 'center',
  },
  searchButtonText: {
    color: '#fff',
    fontWeight: '600',
  },
  listContent: {
    padding: 10,
  },
  volunteerCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  name: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  location: {
    fontSize: 14,
    color: '#666',
    marginBottom: 4,
  },
  skills: {
    fontSize: 14,
    color: '#666',
    marginBottom: 4,
  },
  languages: {
    fontSize: 14,
    color: '#666',
    marginBottom: 4,
  },
  experience: {
    fontSize: 14,
    color: '#666',
    marginBottom: 8,
  },
  statusContainer: {
    marginBottom: 8,
  },
  status: {
    fontSize: 14,
    fontWeight: '600',
  },
  available: {
    color: '#4CAF50',
  },
  unavailable: {
    color: '#FF9800',
  },
  phone: {
    fontSize: 14,
    color: '#007AFF',
    marginTop: 4,
  },
  loadingText: {
    marginTop: 10,
    fontSize: 16,
    color: '#666',
  },
  errorText: {
    fontSize: 16,
    color: '#f44336',
    textAlign: 'center',
    marginBottom: 20,
  },
  retryButton: {
    backgroundColor: '#007AFF',
    paddingHorizontal: 30,
    paddingVertical: 12,
    borderRadius: 8,
  },
  retryButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  emptyContainer: {
    padding: 40,
    alignItems: 'center',
  },
  emptyText: {
    fontSize: 16,
    color: '#999',
  },
});

export default VolunteersScreen;
```

### Step 4: Environment Configuration

Create `.env` file in your React Native project:

```env
# Development
API_URL_DEV=http://localhost:8002

# Production (replace with your actual Coolify URL)
API_URL_PROD=https://your-app.coolify.domain
```

Update your API service to use environment variables:

```javascript
import { API_URL_DEV, API_URL_PROD } from '@env';

const API_URL = __DEV__ ? API_URL_DEV : API_URL_PROD;
```

## Deployment Steps

### 1. Deploy to Coolify

1. Push your code to your git repository
2. Coolify will automatically detect the changes
3. The `volunteer-api` service will be built and deployed
4. Coolify will provide an HTTPS URL for your API

### 2. Update React Native App

1. Get the API URL from Coolify (e.g., `https://your-app.coolify.domain`)
2. Update the `API_URL_PROD` in your React Native `.env` file
3. Rebuild your React Native app

### 3. Test the Connection

```javascript
// Test in your React Native app
import { volunteerApi } from './services/volunteerApi';

// Check API health
volunteerApi.checkHealth()
  .then(data => console.log('API Status:', data))
  .catch(error => console.error('API Error:', error));

// Fetch volunteers
volunteerApi.getVolunteers()
  .then(data => console.log('Volunteers:', data))
  .catch(error => console.error('Error:', error));
```

## Testing Locally

Before deploying, you can test locally:

1. Run the API locally:
   ```bash
   docker-compose up volunteer-api
   ```

2. The API will be available at `http://localhost:8002`

3. Test endpoints:
   ```bash
   # Health check
   curl http://localhost:8002/health
   
   # Get volunteers
   curl http://localhost:8002/api/volunteers
   
   # Search by skill
   curl http://localhost:8002/api/volunteers?skill=cooking
   ```

## Security Considerations

1. **CORS**: The API currently allows all origins (`*`). In production, update [`api.py`](api.py:14) to only allow your React Native app's domain.

2. **Authentication**: Consider adding JWT authentication for production use.

3. **Rate Limiting**: Add rate limiting to prevent abuse.

4. **HTTPS**: Coolify automatically provides HTTPS, always use it in production.

## Troubleshooting

### API Not Responding

1. Check Coolify logs for the `volunteer-api` service
2. Verify environment variables are set correctly
3. Test the health endpoint: `https://your-app.coolify.domain/health`

### Database Connection Issues

1. Verify `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` are correct
2. Check that the API service can reach the Postgres service on the Coolify network
3. Review logs: `docker-compose logs volunteer-api`

### React Native Connection Issues

1. Verify the API URL is correct
2. Check network permissions in your app
3. Test with curl or Postman first
4. Check CORS settings if getting CORS errors

## Next Steps

1. Add authentication (JWT tokens)
2. Implement pagination for large datasets
3. Add caching for better performance
4. Create more specific endpoints as needed
5. Add error tracking (Sentry, etc.)

## Support

For issues or questions:
- Check Coolify logs
- Review API documentation at `https://your-app.coolify.domain/docs` (FastAPI auto-generates docs)
- Test endpoints with the interactive docs at `https://your-app.coolify.domain/docs`