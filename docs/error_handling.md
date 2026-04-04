# Error Handling Architecture

Our web server defines absolute JSON fallbacks for common gateway issues. This ensures that UI consumers or generic API clients always receive a reliable, parseable JSON payload instead of default unhandled HTML error pages.

## Error Topologies

### `404 Not Found`
Any unmapped route (e.g., visiting an unregistered API endpoint or a shortened URL that does not exist in the database) instantly issues the following JSON payload:

```json
{ 
  "error": "Resource not found", 
  "details": "<flask_error_description>" 
}
```

This is accompanied by a valid HTTP `404` status header natively evaluated through the `@app.errorhandler(404)` decorator inside `app/__init__.py`. This prevents unhandled route executions from breaking the application state.

### `500 Internal Server Error`
Should the database crash, a connection timeout occur, or a native Python execution fail fatally, Flask will intercept the fatal exception and execute the following payload:

```json
{ 
  "error": "Internal server error",
  "details": "<flask_error_description>" 
}
```

This is served alongside a proper HTTP `500` status indicator keeping the server application globally alive permanently, while notifying external load balancers and clients exactly why the specific route failed.
