"""
Text Processing Workflows for AI Meeting Assistant
Implements meeting summary, key points, and action items extraction
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

from langchain.prompts import PromptTemplate
from langchain.schema import BaseOutputParser

from .model_manager import get_model_manager, ModelType

logger = logging.getLogger(__name__)


@dataclass
class ProcessingResult:
    """Result of text processing operation"""
    success: bool
    content: str
    processing_time: float
    model_used: str
    word_count: int
    error: Optional[str] = None


class MeetingProcessor:
    """Processes meeting transcripts using LLM workflows"""
    
    # Prompt templates for different processing tasks
    SUMMARY_TEMPLATE = """
You are an expert meeting assistant. Please create a clear, concise summary of the following meeting transcript.

Meeting Transcript:
{transcript}

Please provide:
1. A brief overview (2-3 sentences)
2. Main topics discussed
3. Key decisions made
4. Important outcomes

Summary:"""

    KEY_POINTS_TEMPLATE = """
You are an expert meeting assistant. Extract the key points from this meeting transcript.

Meeting Transcript:
{transcript}

Please extract the most important points discussed in this meeting. Focus on:
- Main topics and themes
- Important decisions
- Significant insights or conclusions
- Key information shared

Format as clear, concise bullet points.

Key Points:"""

    ACTION_ITEMS_TEMPLATE = """
You are an expert meeting assistant. Identify action items from this meeting transcript.

Meeting Transcript:
{transcript}

Please identify all action items, tasks, or follow-up items mentioned in the meeting. For each item, include:
- What needs to be done
- Who is responsible (if mentioned)
- When it should be completed (if mentioned)

If no action items are found, say "No specific action items identified."

Action Items:"""

    MEETING_INSIGHTS_TEMPLATE = """
You are an expert meeting assistant. Analyze this meeting transcript and provide insights.

Meeting Transcript:
{transcript}

Please provide:
1. Meeting tone and sentiment
2. Level of agreement/disagreement
3. Areas needing follow-up
4. Suggested next steps

Meeting Insights:"""

    def __init__(self):
        """Initialize the meeting processor"""
        self.model_manager = get_model_manager()
        
        # Create prompt templates
        self.summary_prompt = PromptTemplate(
            template=self.SUMMARY_TEMPLATE,
            input_variables=["transcript"]
        )
        
        self.key_points_prompt = PromptTemplate(
            template=self.KEY_POINTS_TEMPLATE,
            input_variables=["transcript"]
        )
        
        self.action_items_prompt = PromptTemplate(
            template=self.ACTION_ITEMS_TEMPLATE,
            input_variables=["transcript"]
        )
        
        self.insights_prompt = PromptTemplate(
            template=self.MEETING_INSIGHTS_TEMPLATE,
            input_variables=["transcript"]
        )
    
    def _process_with_model(
        self, 
        transcript: str, 
        prompt_template: PromptTemplate,
        model_type: Optional[ModelType] = None,
        **model_kwargs
    ) -> ProcessingResult:
        """
        Process transcript with specified model and prompt
        
        Args:
            transcript: Meeting transcript text
            prompt_template: LangChain prompt template
            model_type: Model to use (None for default)
            **model_kwargs: Additional model parameters
            
        Returns:
            ProcessingResult with the processed content
        """
        start_time = datetime.now()
        
        try:
            # Use default model if none specified
            if model_type is None:
                model_type = self.model_manager.get_default_model()
            
            if model_type is None:
                return ProcessingResult(
                    success=False,
                    content="",
                    processing_time=0.0,
                    model_used="none",
                    word_count=0,
                    error="No models available"
                )
            
            # Get model instance
            model = self.model_manager.create_model_instance(model_type, **model_kwargs)
            
            # Format prompt
            formatted_prompt = prompt_template.format(transcript=transcript)
            
            # Generate response
            response = model.invoke(formatted_prompt)
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Get model spec for name
            spec = self.model_manager.get_model_spec(model_type)
            model_name = spec.display_name if spec else str(model_type.value)
            
            return ProcessingResult(
                success=True,
                content=response.strip(),
                processing_time=processing_time,
                model_used=model_name,
                word_count=len(response.split())
            )
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Processing failed: {e}")
            
            return ProcessingResult(
                success=False,
                content="",
                processing_time=processing_time,
                model_used="error",
                word_count=0,
                error=str(e)
            )
    
    def create_summary(
        self, 
        transcript: str, 
        model_type: Optional[ModelType] = None
    ) -> ProcessingResult:
        """
        Create a summary of the meeting transcript
        
        Args:
            transcript: Meeting transcript text
            model_type: Model to use for processing
            
        Returns:
            ProcessingResult with the summary
        """
        logger.info("Creating meeting summary...")
        return self._process_with_model(transcript, self.summary_prompt, model_type)
    
    def extract_key_points(
        self, 
        transcript: str, 
        model_type: Optional[ModelType] = None
    ) -> ProcessingResult:
        """
        Extract key points from the meeting transcript
        
        Args:
            transcript: Meeting transcript text
            model_type: Model to use for processing
            
        Returns:
            ProcessingResult with key points
        """
        logger.info("Extracting key points...")
        return self._process_with_model(transcript, self.key_points_prompt, model_type)
    
    def identify_action_items(
        self, 
        transcript: str, 
        model_type: Optional[ModelType] = None
    ) -> ProcessingResult:
        """
        Identify action items from the meeting transcript
        
        Args:
            transcript: Meeting transcript text
            model_type: Model to use for processing
            
        Returns:
            ProcessingResult with action items
        """
        logger.info("Identifying action items...")
        return self._process_with_model(transcript, self.action_items_prompt, model_type)
    
    def generate_insights(
        self, 
        transcript: str, 
        model_type: Optional[ModelType] = None
    ) -> ProcessingResult:
        """
        Generate meeting insights from the transcript
        
        Args:
            transcript: Meeting transcript text
            model_type: Model to use for processing
            
        Returns:
            ProcessingResult with meeting insights
        """
        logger.info("Generating meeting insights...")
        return self._process_with_model(transcript, self.insights_prompt, model_type)
    
    def process_all(
        self, 
        transcript: str, 
        model_type: Optional[ModelType] = None,
        include_insights: bool = False
    ) -> Dict[str, ProcessingResult]:
        """
        Process transcript with all available workflows
        
        Args:
            transcript: Meeting transcript text
            model_type: Model to use for processing
            include_insights: Whether to include insights processing
            
        Returns:
            Dictionary with all processing results
        """
        logger.info("Processing transcript with all workflows...")
        
        results = {
            'summary': self.create_summary(transcript, model_type),
            'key_points': self.extract_key_points(transcript, model_type),
            'action_items': self.identify_action_items(transcript, model_type)
        }
        
        if include_insights:
            results['insights'] = self.generate_insights(transcript, model_type)
        
        return results


# Global processor instance
_meeting_processor: Optional[MeetingProcessor] = None


def get_meeting_processor() -> MeetingProcessor:
    """Get global meeting processor instance"""
    global _meeting_processor
    if _meeting_processor is None:
        _meeting_processor = MeetingProcessor()
    return _meeting_processor


def process_transcript(
    transcript: str,
    processing_type: str = "summary",
    model_name: Optional[str] = None
) -> ProcessingResult:
    """
    Convenience function to process transcript
    
    Args:
        transcript: Meeting transcript text
        processing_type: Type of processing ('summary', 'key_points', 'action_items', 'insights')
        model_name: Name of model to use
        
    Returns:
        ProcessingResult
    """
    processor = get_meeting_processor()
    
    # Convert model name to ModelType
    model_type = None
    if model_name:
        model_type = processor.model_manager.get_model_by_name(model_name)
    
    # Route to appropriate processing method
    if processing_type == "summary":
        return processor.create_summary(transcript, model_type)
    elif processing_type == "key_points":
        return processor.extract_key_points(transcript, model_type)
    elif processing_type == "action_items":
        return processor.identify_action_items(transcript, model_type)
    elif processing_type == "insights":
        return processor.generate_insights(transcript, model_type)
    else:
        return ProcessingResult(
            success=False,
            content="",
            processing_time=0.0,
            model_used="none",
            word_count=0,
            error=f"Unknown processing type: {processing_type}"
        )


if __name__ == "__main__":
    # Test the processor with sample text
    test_transcript = """
    John: Good morning everyone, thanks for joining today's project review meeting.
    Sarah: Thanks John. I wanted to update everyone on the marketing campaign progress.
    We've completed the initial designs and they're ready for review.
    Mike: That's great Sarah. I can review those by Friday. 
    John: Perfect. Mike, can you also look into the budget allocation we discussed?
    Mike: Yes, I'll have that analysis ready by next Tuesday.
    Sarah: Should we schedule a follow-up meeting for next week?
    John: Good idea. Let's meet again next Wednesday at 2 PM.
    """
    
    print("Testing Meeting Processor...")
    
    # Test summary
    result = process_transcript(test_transcript, "summary")
    if result.success:
        print(f"\n✅ Summary (by {result.model_used}):")
        print(result.content)
        print(f"Processing time: {result.processing_time:.2f}s")
    else:
        print(f"❌ Summary failed: {result.error}")
    
    # Test action items
    result = process_transcript(test_transcript, "action_items")
    if result.success:
        print(f"\n✅ Action Items (by {result.model_used}):")
        print(result.content)
    else:
        print(f"❌ Action items failed: {result.error}")
