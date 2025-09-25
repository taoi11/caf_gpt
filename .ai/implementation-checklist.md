# Database Integration Implementation Checklist

## Pre-Implementation Setup
- [x] Create new branch `database-integration`
- [x] Research SvelteKit database schema
- [x] Analyze current Django S3 usage
- [x] Create integration plan

## Phase 1: Database Models (Priority: High)

### Create Database Models
- [ ] Create `core/models/database_models.py`
- [ ] Implement `DoadDocument` model
  - [ ] UUID primary key field
  - [ ] text_chunk TextField
  - [ ] metadata JSONField
  - [ ] created_at DateTimeField
  - [ ] doad_number TextField
  - [ ] Set `managed = False`
  - [ ] Set `db_table = 'doad'`
- [ ] Implement `LeaveDocument` model
  - [ ] UUID primary key field
  - [ ] text_chunk TextField
  - [ ] metadata JSONField
  - [ ] created_at DateTimeField
  - [ ] chapter TextField
  - [ ] Set `managed = False`
  - [ ] Set `db_table = 'leave_2025'`
- [ ] Update `core/models/__init__.py` to import new models
- [ ] Add models to Django admin (optional, for debugging)

### Test Database Connection
- [ ] Create management command to test database connection
- [ ] Verify models can query existing data
- [ ] Test UUID field handling
- [ ] Test JSONB metadata field access

## Phase 2: Database Services (Priority: High)

### Base Database Service
- [ ] Create `core/services/database_service.py`
- [ ] Implement `BasePolicyDatabaseService` class
  - [ ] Database connection handling
  - [ ] Error handling and logging
  - [ ] Common query patterns
  - [ ] Metadata formatting utilities

### DOAD Database Service
- [ ] Implement `DoadDatabaseService` class
  - [ ] `get_doad_content(doad_number: str)` method
  - [ ] `get_available_doads()` method
  - [ ] `get_doad_metadata(doad_number: str)` method
  - [ ] Chunk aggregation logic
  - [ ] Error handling for missing DOADs

### Pace Note Database Service
- [ ] Implement `PaceNoteDatabaseService` class
  - [ ] `get_competency_content(rank: str)` method
  - [ ] `get_examples_content()` method
  - [ ] Rank-to-content mapping logic
  - [ ] Metadata-based content filtering

### Service Integration
- [ ] Update `core/services/__init__.py` to export new services
- [ ] Create service factory/registry if needed
- [ ] Add proper logging configuration
- [ ] Implement connection pooling considerations

## Phase 3: Replace S3 Usage (Priority: High)

### Update DOAD Reader
- [ ] Backup current `policy_foo/views/doad_foo/reader.py`
- [ ] Replace S3Service import with DoadDatabaseService
- [ ] Update `read_doad_content()` function:
  - [ ] Remove S3 key construction
  - [ ] Replace `s3_service.read_file()` with database query
  - [ ] Update error handling for database errors
  - [ ] Maintain same return format (XML string)
  - [ ] Update logging messages
- [ ] Test DOAD reader functionality
- [ ] Verify XML output format remains consistent

### Update Pace Note Services
- [ ] Backup current `pacenote_foo/services/s3_reader.py`
- [ ] Replace S3Service with PaceNoteDatabaseService
- [ ] Update `get_competency_list()` function:
  - [ ] Remove S3 path construction
  - [ ] Replace S3 read with database query
  - [ ] Update rank mapping logic
  - [ ] Maintain same return format
- [ ] Update `get_examples()` function:
  - [ ] Replace S3 read with database query
  - [ ] Maintain same return format
- [ ] Test pace note functionality

### Update Service Imports
- [ ] Update imports in affected view files
- [ ] Remove S3Service imports where no longer needed
- [ ] Update any other files that import S3 services

## Phase 4: Environment & Dependencies (Priority: Medium)

### Environment Variables
- [ ] Verify `DATABASE_URL` is properly configured
- [ ] Document required database permissions (read-only)
- [ ] Remove S3-related environment variables from documentation:
  - [ ] `S3_ENDPOINT_URL`
  - [ ] `S3_BUCKET_NAME`
  - [ ] `AWS_ACCESS_KEY_ID`
  - [ ] `AWS_SECRET_ACCESS_KEY`
  - [ ] `S3_REGION_NAME`

### Dependencies Cleanup
- [ ] Remove `boto3==1.35.30` from `requirements.txt`
- [ ] Test that application still starts without boto3
- [ ] Update any Docker configurations if needed
- [ ] Update deployment documentation

## Phase 5: Code Cleanup (Priority: Low)

### Remove S3 Services
- [ ] Remove `core/services/s3_service.py`
- [ ] Update `core/services/__init__.py` to remove S3Service export
- [ ] Remove any S3-related utility functions
- [ ] Clean up S3-related imports in `__init__.py` files

### Update Documentation
- [ ] Update app README files to reflect database usage
- [ ] Update `.ai/notepad` with database integration notes
- [ ] Document new database services
- [ ] Update deployment instructions

## Phase 6: Testing & Validation (Priority: High)

### Unit Tests
- [ ] Create tests for `DoadDocument` model
- [ ] Create tests for `LeaveDocument` model
- [ ] Create tests for `DoadDatabaseService`
- [ ] Create tests for `PaceNoteDatabaseService`
- [ ] Test error handling scenarios
- [ ] Test with mock database responses

### Integration Tests
- [ ] Test full DOAD retrieval flow
- [ ] Test pace note retrieval flow
- [ ] Test with actual database connection
- [ ] Verify content format matches expectations
- [ ] Test error scenarios (missing documents, connection issues)

### Manual Testing
- [ ] Test DOAD lookup functionality in web interface
- [ ] Test pace note functionality in web interface
- [ ] Verify performance is acceptable
- [ ] Test error handling in UI

## Phase 7: Deployment Preparation (Priority: Medium)

### Database Permissions
- [ ] Verify Django has read-only access to shared database
- [ ] Test connection with production-like environment
- [ ] Document required database permissions
- [ ] Create database user with minimal required permissions

### Configuration
- [ ] Update production environment variables
- [ ] Remove S3 credentials from production
- [ ] Test with production database connection string
- [ ] Verify SSL/TLS configuration for database connection

### Monitoring
- [ ] Add database connection health checks
- [ ] Add logging for database query performance
- [ ] Set up alerts for database connection issues
- [ ] Monitor query performance

## Rollback Plan (Priority: High)

### Backup Strategy
- [ ] Keep S3 services in separate branch
- [ ] Create feature flag to switch between S3 and database
- [ ] Document rollback procedure
- [ ] Test rollback process

### Emergency Procedures
- [ ] Document steps to quickly revert to S3
- [ ] Create emergency deployment procedure
- [ ] Test rollback with minimal downtime
- [ ] Prepare communication plan for users

## Post-Implementation (Priority: Low)

### Performance Optimization
- [ ] Monitor database query performance
- [ ] Implement caching if needed
- [ ] Optimize database queries
- [ ] Consider connection pooling improvements

### Future Enhancements
- [ ] Consider implementing write operations (if needed)
- [ ] Add database migration capabilities
- [ ] Implement data synchronization monitoring
- [ ] Add database backup verification

## Risk Mitigation

### High Risk Items
- [ ] Database connection failures
- [ ] Data format mismatches
- [ ] Performance degradation
- [ ] Missing documents in database

### Mitigation Strategies
- [ ] Implement comprehensive error handling
- [ ] Add fallback mechanisms
- [ ] Create detailed logging
- [ ] Implement health checks
- [ ] Plan for gradual rollout

## Success Criteria

### Functional Requirements
- [ ] All DOAD documents accessible via database
- [ ] All pace note content accessible via database
- [ ] Same user experience as S3-based system
- [ ] Error handling maintains user-friendly messages
- [ ] Performance is acceptable (< 2s response time)

### Technical Requirements
- [ ] No S3 dependencies in codebase
- [ ] Clean, maintainable database service layer
- [ ] Proper error handling and logging
- [ ] Read-only database access
- [ ] Secure database connection

### Operational Requirements
- [ ] Successful deployment to production
- [ ] No data loss or corruption
- [ ] Monitoring and alerting in place
- [ ] Documentation updated
- [ ] Team trained on new system

## Notes
- This is a read-only integration - Django will not write to the shared database
- The SvelteKit app continues to manage the database schema and data
- Focus on maintaining exact same functionality while changing the data source
- Prioritize thorough testing due to the critical nature of document retrieval