# Study Buddy AI 🎓

An intelligent AI-powered quiz generation application that leverages Large Language Models (LLMs) to create customized quizzes on any topic. Built with Streamlit, LangChain, and Groq's Llama model, Study Buddy AI provides an interactive learning experience with automatic question generation, quiz taking, and performance evaluation.

## 📋 Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Development](#development)
- [Deployment](#deployment)
- [CI/CD Pipeline](#cicd-pipeline)
- [API Documentation](#api-documentation)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

### Core Functionality
- **AI-Powered Question Generation**: Automatically generates quiz questions using Groq's Llama 3.1 8B Instant model
- **Multiple Question Types**:
  - Multiple Choice Questions (MCQ) with 4 options
  - Fill-in-the-Blank questions
- **Customizable Quiz Settings**:
  - Adjustable difficulty levels (Easy, Medium, Hard)
  - Configurable number of questions (1-10)
  - Topic-based question generation
- **Interactive Quiz Interface**: User-friendly Streamlit web interface for taking quizzes
- **Automatic Evaluation**: Instant feedback on quiz performance with detailed results
- **Results Export**: Save quiz results to CSV format for later analysis
- **Comprehensive Logging**: Detailed logging system for debugging and monitoring

### Technical Features
- **Retry Mechanism**: Automatic retry logic for robust LLM API calls
- **Error Handling**: Custom exception handling with detailed error messages
- **Modular Architecture**: Clean, maintainable code structure
- **Docker Support**: Containerized application for easy deployment
- **Kubernetes Ready**: Complete Kubernetes manifests for production deployment
- **CI/CD Integration**: Jenkins pipeline for automated builds and deployments
- **GitOps Workflow**: ArgoCD integration for declarative application management

## 🛠 Technology Stack

### Core Technologies
- **Python 3.10**: Primary programming language
- **Streamlit**: Web application framework for the user interface
- **LangChain**: Framework for LLM application development
- **LangChain-Groq**: Groq integration for LangChain
- **Pandas**: Data manipulation and CSV export functionality
- **Pydantic**: Data validation and schema definition

### LLM & AI
- **Groq API**: High-performance inference API
- **Llama 3.1 8B Instant**: Large Language Model for question generation

### DevOps & Infrastructure
- **Docker**: Containerization
- **Kubernetes**: Container orchestration
- **Jenkins**: Continuous Integration/Continuous Deployment
- **ArgoCD**: GitOps continuous delivery tool
- **Minikube**: Local Kubernetes cluster (for development)

### Development Tools
- **python-dotenv**: Environment variable management
- **setuptools**: Package installation and distribution

## 📁 Project Structure

```
STUDY-BUDDY-AI/
├── application.py              # Main Streamlit application entry point
├── Dockerfile                   # Docker container configuration
├── requirements.txt             # Python dependencies
├── setup.py                     # Package setup configuration
├── Jenkinsfile                  # Jenkins CI/CD pipeline definition
├── manifests/                   # Kubernetes deployment manifests
│   ├── deployment.yaml         # Kubernetes deployment configuration
│   └── service.yaml            # Kubernetes service configuration
├── src/                         # Source code directory
│   ├── __init__.py
│   ├── common/                  # Common utilities
│   │   ├── __init__.py
│   │   ├── logger.py           # Logging configuration
│   │   └── custom_exception.py  # Custom exception classes
│   ├── config/                  # Configuration management
│   │   ├── __init__.py
│   │   └── settings.py         # Application settings and environment variables
│   ├── generator/               # Question generation logic
│   │   ├── __init__.py
│   │   └── question_generator.py  # Core question generation class
│   ├── llm/                     # LLM client integration
│   │   ├── __init__.py
│   │   └── groq_client.py      # Groq API client wrapper
│   ├── models/                  # Data models and schemas
│   │   ├── __init__.py
│   │   └── question_schemas.py  # Pydantic models for questions
│   ├── prompts/                 # LLM prompt templates
│   │   ├── __init__.py
│   │   └── templates.py        # Prompt templates for question generation
│   └── utils/                   # Utility functions
│       ├── __init__.py
│       └── helpers.py          # Helper functions and QuizManager class
├── logs/                        # Application logs directory
├── results/                     # Quiz results CSV files
└── venv/                        # Python virtual environment (not in git)
```

## 📦 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.10+**: [Download Python](https://www.python.org/downloads/)
- **pip**: Python package manager (usually comes with Python)
- **Git**: Version control system
- **Docker** (optional, for containerization): [Install Docker](https://docs.docker.com/get-docker/)
- **Kubernetes** (optional, for deployment): [Install kubectl](https://kubernetes.io/docs/tasks/tools/)
- **Groq API Key**: Sign up at [Groq Console](https://console.groq.com/) to get your API key

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/uwadonemmanuel/STUDY-BUDDY-AI.git
cd STUDY-BUDDY-AI
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Or install the package in development mode:

```bash
pip install -e .
```

### 4. Set Up Environment Variables

Create a `.env` file in the root directory:

```bash
touch .env
```

Add your Groq API key to the `.env` file:

```env
GROQ_API_KEY=your_groq_api_key_here
```

**Note**: Never commit your `.env` file to version control. It should be in `.gitignore`.

## ⚙️ Configuration

### Application Settings

The application settings are configured in `src/config/settings.py`. You can customize:

- **MODEL_NAME**: LLM model to use (default: `"llama-3.1-8b-instant"`)
- **TEMPERATURE**: Model temperature for response creativity (default: `0.9`)
- **MAX_RETRIES**: Maximum number of retry attempts for API calls (default: `3`)

### Logging

Logs are automatically saved to the `logs/` directory with daily rotation. Log files are named `log_YYYY-MM-DD.log`.

## 💻 Usage

### Running the Application Locally

1. **Activate your virtual environment** (if not already activated):
   ```bash
   source venv/bin/activate
   ```

2. **Run the Streamlit application**:
   ```bash
   streamlit run application.py
   ```

3. **Access the application**:
   - The application will open automatically in your default web browser
   - If not, navigate to `http://localhost:8501`

### Using the Application

1. **Configure Quiz Settings** (in the sidebar):
   - Select question type: Multiple Choice or Fill in the Blank
   - Enter a topic (e.g., "Indian History", "Python Programming")
   - Choose difficulty level: Easy, Medium, or Hard
   - Set the number of questions (1-10)

2. **Generate Quiz**:
   - Click the "Generate Quiz" button
   - Wait for questions to be generated (this may take a few seconds)

3. **Take the Quiz**:
   - Answer each question as it appears
   - For MCQ: Select one option using radio buttons
   - For Fill-in-the-Blank: Type your answer in the text field

4. **Submit and Review**:
   - Click "Submit Quiz" when finished
   - View your score and detailed results
   - Review correct and incorrect answers

5. **Export Results** (optional):
   - Click "Save Results" to save to CSV
   - Download the CSV file for your records

## 🔧 Development

### Code Structure

The application follows a modular architecture:

- **`application.py`**: Main Streamlit UI and application flow
- **`src/generator/question_generator.py`**: Core question generation logic with retry mechanism
- **`src/llm/groq_client.py`**: Groq API client wrapper
- **`src/models/question_schemas.py`**: Pydantic models for data validation
- **`src/prompts/templates.py`**: Prompt templates for LLM interactions
- **`src/utils/helpers.py`**: QuizManager class and utility functions
- **`src/common/logger.py`**: Centralized logging configuration
- **`src/common/custom_exception.py`**: Custom exception handling

### Adding New Question Types

To add a new question type:

1. Create a new Pydantic model in `src/models/question_schemas.py`
2. Create a prompt template in `src/prompts/templates.py`
3. Add a generation method in `src/generator/question_generator.py`
4. Update the UI in `application.py` to support the new type

### Running Tests

```bash
# Add your test commands here when tests are implemented
pytest tests/
```

## 🐳 Deployment

### Docker Deployment

1. **Build the Docker image**:
   ```bash
   docker build -t study-buddy-ai:latest .
   ```

2. **Run the container**:
   ```bash
   docker run -p 8501:8501 --env-file .env study-buddy-ai:latest
   ```

3. **Access the application**:
   - Navigate to `http://localhost:8501`

### Kubernetes Deployment

#### Prerequisites
- Kubernetes cluster (Minikube, GKE, EKS, etc.)
- `kubectl` configured to access your cluster

#### Deploy to Kubernetes

1. **Create the secret for Groq API key**:
   ```bash
   kubectl create secret generic groq-api-secret \
     --from-literal=GROQ_API_KEY=your_groq_api_key_here \
     -n your-namespace
   ```

2. **Apply the manifests**:
   ```bash
   kubectl apply -f manifests/deployment.yaml
   kubectl apply -f manifests/service.yaml
   ```

3. **Check deployment status**:
   ```bash
   kubectl get deployments -n your-namespace
   kubectl get pods -n your-namespace
   kubectl get services -n your-namespace
   ```

4. **Access the application**:
   - For NodePort service: `http://<node-ip>:<node-port>`
   - Or use port-forwarding:
     ```bash
     kubectl port-forward svc/llmops-service -n your-namespace 8501:80
     ```

## 🔄 CI/CD Pipeline

The project includes a Jenkins CI/CD pipeline configured in `Jenkinsfile`. The pipeline includes:

1. **Checkout**: Pulls code from GitHub repository
2. **Build Docker Image**: Builds the application Docker image
3. **Push to DockerHub**: Pushes the image to DockerHub registry
4. **Install Tools**: Installs kubectl and ArgoCD CLI
5. **Deploy**: Applies Kubernetes manifests and syncs with ArgoCD

### Jenkins Setup

Refer to `FULL_DOCUMENTATION.md` for detailed Jenkins setup instructions, including:
- Jenkins installation and configuration
- GitHub integration
- DockerHub credentials setup
- Kubernetes cluster access configuration
- ArgoCD integration

### ArgoCD Integration

The application supports GitOps workflow with ArgoCD:

1. Connect your GitHub repository to ArgoCD
2. Create an ArgoCD application pointing to the `manifests/` directory
3. Enable automatic sync for continuous deployment
4. The Jenkins pipeline automatically triggers ArgoCD sync after deployment

## 📚 API Documentation

### QuestionGenerator Class

#### Methods

##### `generate_mcq(topic: str, difficulty: str = 'medium') -> MCQQuestion`
Generates a multiple-choice question.

**Parameters**:
- `topic` (str): The topic for the question
- `difficulty` (str): Difficulty level ('easy', 'medium', 'hard')

**Returns**: `MCQQuestion` object with question, options, and correct answer

**Raises**: `CustomException` if generation fails after max retries

##### `generate_fill_blank(topic: str, difficulty: str = 'medium') -> FillBlankQuestion`
Generates a fill-in-the-blank question.

**Parameters**:
- `topic` (str): The topic for the question
- `difficulty` (str): Difficulty level ('easy', 'medium', 'hard')

**Returns**: `FillBlankQuestion` object with question and answer

**Raises**: `CustomException` if generation fails after max retries

### QuizManager Class

#### Methods

##### `generate_questions(generator, topic, question_type, difficulty, num_questions)`
Generates a set of quiz questions.

**Parameters**:
- `generator` (QuestionGenerator): Question generator instance
- `topic` (str): Topic for questions
- `question_type` (str): 'Multiple Choice' or 'Fill in the Blank'
- `difficulty` (str): 'Easy', 'Medium', or 'Hard'
- `num_questions` (int): Number of questions to generate (1-10)

**Returns**: `bool` - True if successful, False otherwise

##### `attempt_quiz()`
Renders the quiz interface in Streamlit.

##### `evaluate_quiz()`
Evaluates user answers and generates results.

##### `generate_result_dataframe() -> pd.DataFrame`
Generates a pandas DataFrame with quiz results.

**Returns**: DataFrame with columns: question_number, question, question_type, user_answer, correct_answer, is_correct, options

##### `save_to_csv(filename_prefix="quiz_results") -> str`
Saves quiz results to a CSV file.

**Parameters**:
- `filename_prefix` (str): Prefix for the filename

**Returns**: Path to saved file, or None if save fails

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add docstrings to all functions and classes
- Write tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting PR

## 📝 License

This project is part of the Andela GenAI LLMOPS study program. Please refer to the repository for license information.

## 🙏 Acknowledgments

- **Groq** for providing high-performance LLM inference
- **LangChain** for the excellent LLM framework
- **Streamlit** for the intuitive web framework
- **Andela** for the GenAI LLMOPS program

## 📞 Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Contact the maintainers

## 🔗 Links

- **GitHub Repository**: [STUDY-BUDDY-AI](https://github.com/uwadonemmanuel/STUDY-BUDDY-AI)
- **Groq Console**: [console.groq.com](https://console.groq.com/)
- **Streamlit Documentation**: [docs.streamlit.io](https://docs.streamlit.io/)
- **LangChain Documentation**: [python.langchain.com](https://python.langchain.com/)

---

**Made with ❤️ for learning and education**

