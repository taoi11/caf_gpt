# Project Progress and Next Steps

## Completed Tasks
- [x] Set up Django project structure with three apps (Core, PaceNoteFoo, PolicyFoo)
- [x] Configure settings with modular structure (base.py and environment-specific settings)
- [x] Configure security headers middleware
- [x] Set up logging configuration
- [x] Configure database connection to Neon DB PostgreSQL
- [x] Implement landing page view and template
- [x] Create health check endpoint
- [x] Implement Pace Notes UI with HTML, CSS, and JavaScript
- [x] Set up environment variable configuration with python-dotenv
- [x] Update project documentation
- [x] Set up NixOS development environment for local development
- [x] Create place holder Dockerfile and docker-compose.yml
- [x] Implement Open Router service in Core app
- [x] Implement PaceNote generator API endpoint
- [x] Implement prompt template handling for PaceNote generation
- [x] Integrate with S3 for competency lists and examples
- [x] Implement PolicyFoo app models structure (skeleton)
- [x] Create basic UI template for PolicyFoo document search
- [x] Implement server-side rate limiting (RateLimitService)
- [x] Implement ChatInterfaceView and template
- [x] Create PolicyRetrieverView (API endpoint)

## Current Sprint

### Core App
- [x] Create API client base class (S3Service and OpenRouterService)
- [x] Implement Open Router service for LLM integration
- [x] Add IP-based rate limiting (RateLimitService)

### PaceNoteFoo App
- [x] Implement backend API for Pace Notes generation
- [x] Connect to an LLM provider (Open Router with Claude 3.5 Haiku)
- [x] Implement server-side rate limiting
- [x] Add data validation for user input
- [x] Create response formatting for pace notes

### PolicyFoo App
- [x] Create basic data models for policy documents, queries and responses
- [x] Create document search UI template
- [x] Implement ChatInterfaceView
- [x] Set up PolicyRetriever service (initial implementation)
- [ ] Implement citation support for answers
- [ ] Add document upload functionality

## Backlog

### Core App
- [x] Add IP-based rate limiting
- [x] Implement rate limit helper functions
- [ ] Add basic security tests
- [ ] Add caching for S3 resources

### PaceNoteFoo App
- [x] Integrate LLM client
- [x] Implement data validation/sanitization
- [x] Add more rank options with corresponding competency lists
- [ ] Add privacy respecting analytics for tracking usage patterns

### PolicyFoo App
- [x] Implement ChatInterfaceView
- [x] Create document search template
- [x] Create DocumentSearchView functionality
- [x] Set up PolicyRetriever service
- [x] Add basic chat template
- [ ] Implement CitationExtractor
- [ ] Add export capability
- [ ] Set up response validation
- [ ] Configure policy document sources

### Infrastructure
- [ ] Configure deployment settings
- [ ] Set up monitoring

### Documentation
- [x] Update PaceNote app documentation
- [ ] Create API documentation

## Technical Debt
- [ ] Add comprehensive test coverage
- [ ] Add API documentation
- [ ] Write security guidelines

### Infrastructure
- [ ] Implement basic CI/CD pipeline
    - Docker build and push to Docker Hub
    - Github actions

## Decision Log
- Use NixOS for local development
- Use Docker for production deployment
- Use Custom CSS instead of Bootstrap
- Use modular settings structure
- Use Neon DB for PostgreSQL
- Use Python slim Docker image
- Use core app for all shared functionality and reusable components
- Use Open Router LLM provider and model selection at the agent/service level
- Implement IP-based rate limiting

