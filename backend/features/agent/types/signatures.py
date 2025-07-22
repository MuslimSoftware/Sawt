import dspy
from dspy import History


class ConversationSig(dspy.Signature):
    """
    You are a helpful voice assistant that can answer general questions conversationally.
    You respond with plain conversational text, no markdown or code or any special characters.
    Your responses should be in clear conversational style, so that it can be converted to speech without problems.
    Also you should determine if the user is speaking to you or whether the transciption is non-sensical or doesnt make any sense. in those cases you should respond with [Not directed at agent]
    """
    user_utterance: str = dspy.InputField(desc="What the user just said, as plain text from speech.")
    conversation_history: History = dspy.InputField(desc="Previous turns of the voice conversation.")
    assistant_utterance: str = dspy.OutputField(desc="How the assistant should speak back – plain conversational text, no markdown or code or special characters. Respond in short sentences and paragraphs. Maximum 3-4 sentences.")
    is_directed_at_agent: bool = dspy.OutputField(desc="Whether the user's utterance is directed at the agent. If the user is clearly speaking to you and the transcription is not non-sensical or doesnt make any sense, then this should be True. If the user is speaking to you and the transcription is non-sensical or doesnt make any sense, then this should be False.")
