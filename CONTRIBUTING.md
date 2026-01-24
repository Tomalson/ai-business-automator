# Contributing Guidelines

Thanks for your interest in contributing to **AI Business Automator**! 🎉

## How to Contribute

### 1. Fork & Clone
```bash
git clone https://github.com/YOUR_USERNAME/ai-business-automator.git
cd ai-business-automator
```

### 2. Create Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### 3. Make Changes
- Follow PEP 8 style guide
- Write tests for new features
- Update README if needed

### 4. Run Tests
```bash
pytest test_main.py test_services.py -v --cov=.
```

### 5. Commit & Push
```bash
git commit -m "feat: add your feature description"
git push origin feature/your-feature-name
```

### 6. Create Pull Request
- Describe changes clearly
- Reference related issues
- Ensure all tests pass

## Commit Message Format

```
type(scope): subject

body

footer
```

**Types:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `test:` Tests
- `refactor:` Code refactor
- `ci:` CI/CD changes

**Example:**
```
feat(ai-service): add profanity filtering

Adds profanity detection to prevent spam leads from being scored highly.

Fixes #42
```

## Code Style

- Use type hints where possible
- Follow PEP 8
- Max line length: 120 characters
- Use meaningful variable names

## Testing

All PRs must include tests:
- Unit tests for new functions
- Integration tests for API changes
- Maintain >80% code coverage

## Questions?

Open an issue or contact the maintainer.

Happy coding! 🚀
