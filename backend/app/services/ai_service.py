import logging
from app.config import Config
from app.utils.vector_store import vector_store
from app.utils.file_processor import chunk_text, clean_text

# Import Groq API
try:
    from groq import Groq
except ImportError:
    Groq = None
    
logger = logging.getLogger(__name__)

class AIService:
    """AI service with RAG integration using Groq Mixtral"""
    
    def __init__(self):
        self.api_key = Config.GROQ_API_KEY
        self.model_name = "llama-3.3-70b-versatile"  # Updated: 3.1-70b was decommissioned by Groq
        self.vector_store = vector_store
        self.max_retries = 3
        self.client = None
        
        if not self.api_key:
            logger.warning("GROQ_API_KEY not found in environment variables")
        elif Groq:
            try:
                self.client = Groq(api_key=self.api_key)
                logger.info("Groq client initialized successfully")
            except Exception as e:
                logger.error(f"Error initializing Groq client: {e}")
        else:
            logger.warning("groq package not installed. Run: pip install groq")
    
    def check_model_available(self):
        """Check if Groq API is available"""
        try:
            if not self.api_key or not self.client:
                return False
            # Test with a simple message
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": "test"}],
                model=self.model_name,
                max_tokens=50,
            )
            return response is not None
        except Exception as e:
            logger.error(f"Error checking model availability: {e}")
            return False
    
    def generate_response(self, prompt, context=None, temperature=0.7):
        """Generate response using Groq Mixtral with RAG"""
        try:
            if not self.api_key:
                return {
                    'success': False,
                    'error': 'API key not configured. Please set GROQ_API_KEY in .env',
                    'fallback': True
                }
            
            if not self.client:
                return {
                    'success': False,
                    'error': 'Groq client not initialized. Check your API key.',
                    'fallback': True
                }
            
            # Prepare context from vector store
            rag_context = ""
            if context:
                search_results = self.vector_store.search(context, top_k=3)
                if search_results:
                    rag_context = "\n\n".join([
                        f"Reference: {result['text']}"
                        for result in search_results
                    ])
            
            # Build prompt with context
            full_prompt = self._build_prompt(prompt, rag_context)
            
            # Call Groq API
            response = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": full_prompt
                    }
                ],
                model=self.model_name,
                temperature=temperature,
                max_tokens=1024,
                top_p=0.95,
            )
            
            if response and response.choices and response.choices[0].message.content:
                return {
                    'success': True,
                    'response': response.choices[0].message.content.strip(),
                    'tokens_used': 0
                }
            else:
                logger.error(f"Groq returned empty response")
                return self._fallback_response(prompt)
        
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error generating response: {error_msg}")
            # Check for rate limit or other errors
            if 'rate_limit' in error_msg.lower():
                return {
                    'success': False,
                    'error': 'Rate limit reached. Please try again in a moment.',
                    'fallback': True
                }
            elif 'invalid_api_key' in error_msg.lower() or 'authentication' in error_msg.lower():
                return {
                    'success': False,
                    'error': 'Invalid API key. Please check your GROQ_API_KEY in .env',
                    'fallback': True
                }
            return self._fallback_response(prompt)
    
    def _build_prompt(self, user_prompt, context=""):
        """Build system prompt with context"""
        system_message = """You are an intelligent educational assistant helping students learn. 
Your responses should be:
- Clear and easy to understand
- Focused on the subject matter
- Encouraging and supportive
- Accurate based on provided context
- Well-structured with examples when helpful

If you don't know something, say so honestly."""
        
        if context:
            prompt = f"""{system_message}

Context from course materials:
{context}

Student Question: {user_prompt}

Provide a helpful, syllabus-aligned response:"""
        else:
            prompt = f"""{system_message}

Student Question: {user_prompt}

Provide a helpful response:"""
        
        return prompt
    
    def _fallback_response(self, prompt):
        """Provide fallback response when model fails"""
        fallback_responses = {
            'explain': 'I understand you want an explanation. Could you be more specific about what topic?',
            'summarize': 'I can help summarize. Please provide the text or topic you want summarized.',
            'example': 'Let me help with examples. What specific concept would you like examples for?',
            'quiz': 'I can generate a quiz! What subject or topic would you like?',
        }
        
        prompt_lower = prompt.lower()
        for key, response in fallback_responses.items():
            if key in prompt_lower:
                return {
                    'success': True,
                    'response': response,
                    'fallback': True
                }
        
        return {
            'success': True,
            'response': "I'm currently unable to fully process your request. Please try again or ask about a specific topic.",
            'fallback': True
        }
    
    def generate_quiz(self, topic, num_questions=5, difficulty='medium'):
        """Generate quiz questions"""
        try:
            prompt = f"""Generate {num_questions} quiz questions about "{topic}" at {difficulty} difficulty level.
            
Format each question as:
Q1: [question text]
A) [option 1]
B) [option 2]
C) [option 3]
D) [option 4]
Correct Answer: [A/B/C/D]
Explanation: [brief explanation]

---

Generate the questions:"""
            
            response = self.generate_response(prompt)
            
            if response['success']:
                questions = self._parse_quiz_response(response['response'])
                return {
                    'success': True,
                    'questions': questions
                }
            return response
        except Exception as e:
            logger.error(f"Error generating quiz: {e}")
            return {
                'success': False,
                'error': 'Could not generate quiz'
            }
    
    def _parse_quiz_response(self, response_text):
        """Parse quiz generation response"""
        questions = []
        current_question = {}
        
        lines = response_text.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('Q'):
                if current_question:
                    questions.append(current_question)
                current_question = {'question': line.split(':', 1)[-1].strip()}
            elif line.startswith(('A)', 'B)', 'C)', 'D)')):
                if 'options' not in current_question:
                    current_question['options'] = []
                current_question['options'].append(line)
            elif line.startswith('Correct Answer:'):
                current_question['correct_answer'] = line.split(':')[-1].strip()
            elif line.startswith('Explanation:'):
                current_question['explanation'] = line.split(':', 1)[-1].strip()
        
        if current_question:
            questions.append(current_question)
        
        return questions
    
    def check_answer(self, question, student_answer, correct_answer):
        """Evaluate student answer"""
        try:
            prompt = f"""Evaluate this student's answer:
Question: {question}
Student Answer: {student_answer}
Correct Answer: {correct_answer}

Provide:
1. Is it correct? (Yes/No)
2. Score (0-100)
3. Feedback for the student

Format:
Correct: [Yes/No]
Score: [0-100]
Feedback: [detailed feedback]"""
            
            response = self.generate_response(prompt)
            return response
        except Exception as e:
            logger.error(f"Error checking answer: {e}")
            return {
                'success': False,
                'error': 'Could not evaluate answer'
            }
    
    def add_learning_material(self, document_id, text):
        """Add learning material to vector store"""
        try:
            # Clean and chunk text
            cleaned_text = clean_text(text)
            chunks = chunk_text(cleaned_text, chunk_size=500, overlap=50)
            
            # Add to vector store
            for i, chunk in enumerate(chunks):
                self.vector_store.add_document(
                    f"{document_id}_chunk_{i}",
                    chunk,
                    {'source_id': str(document_id), 'chunk': i}
                )
            
            # Save vector store
            self.vector_store.save()
            
            return {
                'success': True,
                'chunks_added': len(chunks)
            }
        except Exception as e:
            logger.error(f"Error adding learning material: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def remove_learning_material(self, document_id):
        """Remove learning material from vector store"""
        try:
            # Find and remove all chunks for this document
            if self.vector_store.use_faiss:
                self.vector_store.documents = [
                    d for d in self.vector_store.documents
                    if d['metadata'].get('source_id') != str(document_id)
                ]
            else:
                to_delete = [
                    doc_id for doc_id, doc_data in self.vector_store.embeddings_dict.items()
                    if doc_data['metadata'].get('source_id') == str(document_id)
                ]
                for doc_id in to_delete:
                    self.vector_store.delete_document(doc_id)
            
            self.vector_store.save()
            return {'success': True}
        except Exception as e:
            logger.error(f"Error removing learning material: {e}")
            return {'success': False, 'error': str(e)}

# Global AI service instance
ai_service = AIService()
