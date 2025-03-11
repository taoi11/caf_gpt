# Project TODO List

## Core App
### High Priority
- [x] Set up Django project structure
- [ ] Implement LandingPageView
- [ ] Create HealthCheckView
- [x] Configure SecurityHeadersMiddleware
- [ ] Set up base templates and styles
- [x] Configure logger
- [ ] Create API client base class

### Medium Priority
- [ ] Add IP-based rate limiting
- [ ] Implement rate limit helper functions
- [x] Set up environment variable configuration
- [ ] Add basic security tests

## PaceNoteFoo App
### High Priority
- [ ] Create ChatInterfaceView
- [ ] Implement RagSearchView
- [ ] Set up RagRetriever service
- [ ] Create basic chat template

### Medium Priority
- [ ] Integrate LLM client
- [ ] Implement data validation/sanitization
- [ ] Add RAG data sources
- [ ] Create response formatting

## PolicyFoo App
### High Priority
- [ ] Implement ChatInterfaceView
- [ ] Create DocumentSearchView
- [ ] Set up PolicyRetriever service
- [ ] Add basic chat template

### Medium Priority
- [ ] Implement CitationGenerator
- [ ] Add export capability
- [ ] Set up response validation
- [ ] Configure policy document sources

## Infrastructure
### High Priority
- [x] Set up Docker configuration (using Nix instead)
- [x] Configure Postgres database
- [x] Create environment variables setup
- [ ] Implement basic CI/CD pipeline

### Medium Priority
- [ ] Configure deployment settings
- [ ] Set up monitoring
- [ ] Implement backup strategy

## Documentation
- [x] Add project overview documentation
- [ ] Create API documentation
- [x] Add setup instructions
- [ ] Write security guidelines

## Open Questions
### Core
- [ ] Decide on analytics tracking for landing page
- [x] Determine rate limit configuration approach (simplified for now)

### PaceNoteFoo
- [ ] Identify specific RAG data sources
- [ ] Determine response formatting needs
- [ ] Define safety controls for generated content

### PolicyFoo
- [ ] Identify required policy documents
- [ ] Determine response format requirements
- [ ] Define audit requirements
