# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-01-24

### Added
- Initial release of AI Business Automator
- FastAPI REST API for lead processing
- Groq AI integration for lead structuring
- Supabase database persistence
- Docker & Docker Compose support
- Comprehensive pytest test suite (17 tests)
- GitHub Actions CI/CD pipeline
- Multi-stage Dockerfile with security best practices
- Health check monitoring
- CORS middleware configuration
- Niche-based prompt routing
- Environment variable configuration

### Features
- Extract structured data from unstructured text (name, email, phone, product, etc.)
- Lead scoring system (1-10 scale)
- Language consistency in output
- Non-root Docker user for security
- 80%+ code coverage with pytest

### Infrastructure
- Production-ready Docker image (~200MB)
- Automated testing on push/PR
- Codecov integration for coverage tracking
- Docker image building in CI/CD

## [Unreleased]

### Planned
- GraphQL API support
- Advanced lead segmentation
- Webhook integrations
- Rate limiting
- API key management
- Dashboard UI

---

## Version History Format

### [X.Y.Z] - YYYY-MM-DD

#### Added
- New features

#### Changed
- Changes in existing functionality

#### Deprecated
- Soon-to-be removed features

#### Removed
- Removed features

#### Fixed
- Bug fixes

#### Security
- Security updates
