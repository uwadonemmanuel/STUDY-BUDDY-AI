import os
import streamlit as st
from dotenv import load_dotenv
from src.utils.helpers import *
from src.generator.question_generator import QuestionGenerator
load_dotenv()


def main():
    st.set_page_config(page_title="Study Buddy AI" , page_icon="🎧🎧")

    if 'quiz_manager'not in st.session_state:
        st.session_state.quiz_manager = QuizManager()

    if 'quiz_generated'not in st.session_state:
        st.session_state.quiz_generated = False

    if 'quiz_submitted'not in st.session_state:
        st.session_state.quiz_submitted = False

    if 'rerun_trigger'not in st.session_state:
        st.session_state.rerun_trigger = False
        

    st.title("Study Buddy AI")
    st.markdown("### AI-Powered Quiz Generator with Multi-Model Support")

    st.sidebar.header("AI Model Settings")
    
    # Model Provider Selection
    provider = st.sidebar.selectbox(
        "Select AI Provider",
        ["groq", "openai"],
        index=0,
        help="Choose the AI provider for question generation"
    )
    
    # Model Selection based on provider
    from src.config.settings import settings
    available_models = settings.AVAILABLE_MODELS.get(provider, [])
    
    if available_models:
        model_name = st.sidebar.selectbox(
            "Select Model",
            available_models,
            index=0,
            help=f"Available {provider.upper()} models"
        )
    else:
        model_name = settings.DEFAULT_MODEL
        st.sidebar.warning(f"No models available for {provider}")
    
    # Chatbot Persona Selection
    persona_options = {key: value["name"] for key, value in settings.CHATBOT_PERSONAS.items()}
    selected_persona_key = st.sidebar.selectbox(
        "Select Chatbot Persona",
        options=list(persona_options.keys()),
        format_func=lambda x: f"{persona_options[x]} - {settings.CHATBOT_PERSONAS[x]['description']}",
        index=0,
        help="Choose the personality style for question generation"
    )
    
    # Display selected persona description
    if selected_persona_key in settings.CHATBOT_PERSONAS:
        with st.sidebar.expander("Persona Details"):
            st.write(f"**{settings.CHATBOT_PERSONAS[selected_persona_key]['name']}**")
            st.caption(settings.CHATBOT_PERSONAS[selected_persona_key]['description'])

    st.sidebar.header("Quiz Settings")

    question_type = st.sidebar.selectbox(
        "Select Question Type" ,
        ["Multiple Choice" , "Fill in the Blank"],
        index=0
    )

    topic = st.sidebar.text_input("Enter Topic" , placeholder="Indian History, geography")

    difficulty = st.sidebar.selectbox(
        "Difficulty Level",
        ["Easy" , "Medium" , "Hard"],
        index=1
    )

    num_questions=st.sidebar.number_input(
        "Number of Questions",
        min_value=1,  max_value=10 , value=5
    )
    
    # Temperature setting - only show for models that support it
    # Reasoning models (o3, o4-mini) don't support temperature
    reasoning_models = [
        "o3", "o4-mini"
    ]
    supports_temperature = model_name.lower() not in [m.lower() for m in reasoning_models]
    
    if supports_temperature:
        temperature = st.sidebar.slider(
            "Temperature (Creativity)",
            min_value=0.0,
            max_value=2.0,
            value=0.9,
            step=0.1,
            help="Higher values make output more creative, lower values more focused. Not available for reasoning models."
        )
    else:
        # Reasoning models don't support temperature, use None (will use default)
        temperature = None
        st.sidebar.info(f"ℹ️ {model_name} is a reasoning model and doesn't support temperature adjustment.")

    

    
    if st.sidebar.button("Generate Quiz"):
        st.session_state.quiz_submitted = False
        
        # Display selected settings
        with st.spinner(f"Generating quiz using {provider.upper()} {model_name} with {settings.CHATBOT_PERSONAS[selected_persona_key]['name']} persona..."):
            generator = QuestionGenerator(
                provider=provider,
                model_name=model_name,
                temperature=temperature,
                persona=selected_persona_key
            )
            success = st.session_state.quiz_manager.generate_questions(
                generator,
                topic, question_type, difficulty, num_questions
            )

        st.session_state.quiz_generated = success
        if success:
            st.success(f"✅ Quiz generated successfully using {provider.upper()} {model_name}!")
        rerun()

    if st.session_state.quiz_generated and st.session_state.quiz_manager.questions:
        st.header("Quiz")
        st.session_state.quiz_manager.attempt_quiz()

        if st.button("Submit Quiz"):
            st.session_state.quiz_manager.evaluate_quiz()
            st.session_state.quiz_submitted = True
            rerun()

    if st.session_state.quiz_submitted:
        st.header("Quiz Results")
        results_df = st.session_state.quiz_manager.generate_result_dataframe()

        if not results_df.empty:
            correct_count = results_df["is_correct"].sum()
            total_questions = len(results_df)
            score_percentage = (correct_count/total_questions)*100
            st.write(f"Score : {score_percentage}")

            for _, result in results_df.iterrows():
                question_num = result['question_number']
                if result['is_correct']:
                    st.success(f"✅ Question {question_num} : {result['question']}")
                    st.write(f"Your answer : {result['user_answer']}")
                    st.write(f"Correct answer : {result['correct_answer']}")
                else:
                    st.error(f"❌ Question {question_num} : {result['question']}")
                    st.write(f"Your answer : {result['user_answer']}")
                    st.write(f"Correct answer : {result['correct_answer']}")
                
                st.markdown("-------")

            
            if st.button("Save Results"):
                saved_file = st.session_state.quiz_manager.save_to_csv()
                if saved_file:
                    with open(saved_file,'rb') as f:
                        st.download_button(
                            label="Downlaod Results",
                            data=f.read(),
                            file_name=os.path.basename(saved_file),
                            mime='text/csv'
                        )
                else:
                    st.warning("No results avialble")

if __name__=="__main__":
    main()

        
