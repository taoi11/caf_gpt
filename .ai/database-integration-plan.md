# Database Integration Plan: SvelteKit to Django Migration

## Overview
Migrate Django app from S3 document storage to shared PostgreSQL database with SvelteKit app.

## Current State Analysis

### SvelteKit App (Source)
- **Database**: PostgreSQL via Cloudflare Hyperdrive
- **ORM**: Drizzle ORM with TypeScript
- **Connection**: `DATABASE_URL` environment variable
- **Schema**: 
  - `doad` table: id (uuid), text_chunk (text), metadata (jsonb), created_at (timestamp), doad_number (text)
  - `leave_2025` table: id (uuid), text_chunk (text), metadata (jsonb), created_at (timestamp), chapter (text)

### Django App (Target)
- **Database**: PostgreSQL (already configured with `DATABASE_URL`)
- **Current Storage**: S3 (Storj) for documents
- **S3 Usage**:
  - DOAD documents: `doad/{number}.md` files
  - Pace note competencies: `paceNote/{rank}.md` files
- **Dependencies**: boto3, psycopg2-binary

## Integration Strategy

### Phase 1: Database Models Creation
1. Create Django models that mirror the SvelteKit schema
2. Use `managed = False` to prevent Django from trying to create/modify tables
3. Map UUID fields correctly
4. Handle JSONB metadata fields

### Phase 2: Database Service Layer
1. Create database service classes to replace S3 services
2. Implement read-only database operations
3. Add proper error handling and logging
4. Create query methods for document retrieval

### Phase 3: Replace S3 Usage
1. Update DOAD reader to use database instead of S3
2. Update pace note services to use database instead of S3
3. Modify document retrieval logic
4. Update error handling

### Phase 4: Cleanup
1. Remove S3 service dependencies
2. Remove boto3 from requirements.txt
3. Remove S3-related environment variables
4. Clean up unused code

## Database Schema Mapping

### DOAD Documents
```sql
-- SvelteKit Schema
CREATE TABLE doad (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    text_chunk TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    doad_number TEXT
);
```

```python
# Django Model
class DoadDocument(models.Model):
    id = models.UUIDField(primary_key=True)
    text_chunk = models.TextField()
    metadata = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField()
    doad_number = models.TextField(null=True, blank=True)
    
    class Meta:
        managed = False  # Don't let Django manage this table
        db_table = 'doad'
```

### Leave Documents
```sql
-- SvelteKit Schema
CREATE TABLE leave_2025 (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    text_chunk TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    chapter TEXT NOT NULL
);
```

```python
# Django Model
class LeaveDocument(models.Model):
    id = models.UUIDField(primary_key=True)
    text_chunk = models.TextField()
    metadata = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField()
    chapter = models.TextField()
    
    class Meta:
        managed = False  # Don't let Django manage this table
        db_table = 'leave_2025'
```

## Service Layer Design

### Base Database Service
```python
class BasePolicyDatabaseService:
    """Base service for database operations"""
    
    def get_chunks_by_identifier(self, identifier: str, model_class):
        """Get all chunks for a specific identifier"""
        pass
    
    def get_metadata_by_identifier(self, identifier: str, model_class):
        """Get metadata for selection purposes"""
        pass
```

### DOAD Database Service
```python
class DoadDatabaseService(BasePolicyDatabaseService):
    """Service for DOAD document operations"""
    
    def get_doad_content(self, doad_number: str) -> str:
        """Get full DOAD document content by number"""
        pass
    
    def get_available_doads(self) -> List[str]:
        """Get list of available DOAD numbers"""
        pass
```

### Pace Note Database Service
```python
class PaceNoteDatabaseService(BasePolicyDatabaseService):
    """Service for pace note operations"""
    
    def get_competency_content(self, rank: str) -> str:
        """Get competency content for a rank"""
        pass
    
    def get_examples_content(self) -> str:
        """Get examples content"""
        pass
```

## Migration Steps

### Step 1: Create Models
- [ ] Create `core/models/database_models.py`
- [ ] Define DoadDocument and LeaveDocument models
- [ ] Add models to Django apps

### Step 2: Create Database Services
- [ ] Create `core/services/database_service.py`
- [ ] Implement base database service
- [ ] Create DOAD-specific service
- [ ] Create pace note-specific service

### Step 3: Update DOAD Reader
- [ ] Modify `policy_foo/views/doad_foo/reader.py`
- [ ] Replace S3Service with DoadDatabaseService
- [ ] Update document retrieval logic
- [ ] Test DOAD functionality

### Step 4: Update Pace Note Services
- [ ] Modify `pacenote_foo/services/s3_reader.py`
- [ ] Replace S3 calls with database queries
- [ ] Update rank-to-content mapping
- [ ] Test pace note functionality

### Step 5: Environment Variables
- [ ] Ensure `DATABASE_URL` is properly configured
- [ ] Remove S3-related environment variables:
  - `S3_ENDPOINT_URL`
  - `S3_BUCKET_NAME`
  - `AWS_ACCESS_KEY_ID`
  - `AWS_SECRET_ACCESS_KEY`
  - `S3_REGION_NAME`

### Step 6: Dependencies Cleanup
- [ ] Remove `boto3` from requirements.txt
- [ ] Remove S3 service files
- [ ] Update imports across the codebase
- [ ] Remove unused S3 configuration

## Data Mapping Strategy

### DOAD Documents
- **Current**: S3 files `doad/{number}.md` containing full document
- **New**: Database query for `doad_number` returning concatenated `text_chunk` fields
- **Aggregation**: Combine multiple chunks for same `doad_number` ordered by `created_at`

### Pace Note Competencies
- **Current**: S3 files `paceNote/{rank}.md`
- **New**: Database query using metadata to identify rank-specific content
- **Mapping**: Use metadata field to identify rank and content type

## Error Handling

### Database Connection Issues
- Implement connection retry logic
- Graceful degradation when database is unavailable
- Proper logging for debugging

### Missing Documents
- Handle cases where DOAD numbers don't exist in database
- Provide meaningful error messages
- Maintain backward compatibility with existing error responses

## Testing Strategy

### Unit Tests
- Test database service methods
- Mock database responses
- Test error handling scenarios

### Integration Tests
- Test full document retrieval flow
- Test with actual database connection
- Verify content matches expected format

## Rollback Plan

### If Issues Arise
1. Keep S3 services as backup during transition
2. Feature flag to switch between S3 and database
3. Ability to quickly revert to S3 if needed

## Performance Considerations

### Database Queries
- Index on `doad_number` and `chapter` fields
- Efficient aggregation of text chunks
- Connection pooling for Django

### Caching
- Consider caching frequently accessed documents
- Cache metadata for quick lookups
- Implement cache invalidation strategy

## Security Considerations

### Read-Only Access
- Ensure Django only has read permissions
- No write operations to shared database
- Proper connection string configuration

### Data Validation
- Validate document identifiers before queries
- Sanitize user inputs
- Proper error handling without exposing internals