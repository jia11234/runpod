import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig, pipeline
from langchain_huggingface import HuggingFacePipeline, HuggingFaceEmbeddings


def load_models():
    tokenizer = AutoTokenizer.from_pretrained(
        "LGAI-EXAONE/EXAONE-3.5-2.4B-Instruct", 
        trust_remote_code=True 
    )

    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16
    )

    model = AutoModelForCausalLM.from_pretrained(
    "LGAI-EXAONE/EXAONE-3.5-2.4B-Instruct",
    device_map="auto",
    torch_dtype=torch.bfloat16,
    trust_remote_code=True,
    attn_implementation="sdpa"
)

    pipe_analyzer = pipeline(
        'text-generation',
        model=model,
        tokenizer=tokenizer,
        return_full_text=False,
        max_new_tokens=512,
        max_length=None,
        do_sample=False,
        eos_token_id=tokenizer.eos_token_id,
        pad_token_id=tokenizer.pad_token_id
    )

    pipe_generator = pipeline(
        'text-generation',
        model=model,
        tokenizer=tokenizer,
        return_full_text=False,
        max_new_tokens=1024,
        max_length=None,
        do_sample=True,
        temperature=0.7,
        eos_token_id=tokenizer.eos_token_id,
        pad_token_id=tokenizer.pad_token_id
    )

    return {
        "analyzer": HuggingFacePipeline(pipeline=pipe_analyzer),
        "generator": HuggingFacePipeline(pipeline=pipe_generator),
        "tokenizer": tokenizer
    }

def load_embeddings():
    return HuggingFaceEmbeddings(
        model_name='nlpai-lab/KURE-v1',
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )