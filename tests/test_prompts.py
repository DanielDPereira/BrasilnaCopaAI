from app.rag.prompts import get_prompt_template, SYSTEM_PROMPT

def test_prompt_template_formatting():
    template = get_prompt_template()
    formatted = template.format_messages(
        context="O Brasil tem 5 títulos da Copa do Mundo.",
        question="Quantos títulos o Brasil possui?"
    )
    
    assert len(formatted) == 2
    
    # Mensagem do sistema (instruções + contexto)
    sys_msg = formatted[0].content
    assert "Você é um assistente de IA especialista" in sys_msg
    assert "O Brasil tem 5 títulos da Copa do Mundo." in sys_msg
    
    # Mensagem do usuário (pergunta)
    human_msg = formatted[1].content
    assert human_msg == "Quantos títulos o Brasil possui?"
