from google import genai
from google.genai import types
import wave
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up the wave file to save the output:
def wave_file(filename, pcm, channels=1, rate=24000, sample_width=2):
   with wave.open(filename, "wb") as wf:
      wf.setnchannels(channels)
      wf.setsampwidth(sample_width)
      wf.setframerate(rate)
      wf.writeframes(pcm)

# Verify API key is loaded
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in .env file!")

print(f"✓ API key loaded: {api_key[:10]}...")

client = genai.Client(api_key=api_key)

response = client.models.generate_content(
   model="gemini-2.5-flash-preview-tts",
   contents="""Speak in engaging and excited tone: 🧠 AI ANALYSIS REPORT
    Generated: 2025-10-31 13:19:24
    Time Filter: day
    Model: gemini-2.5-pro
    Posts Analyzed: 26
    Subreddits: LocalLLaMA, artificial, MachineLearning, OpenAI, AI_Agents, ArtificialInteligence

    AI ANALYSIS

    ### **Reddit Research Analysis for an AI Engineer**

    This analysis synthesizes insightful discussions from Reddit, focusing on new models, novel techniques, performance benchmarks, and industry trends relevant to AI Engineers.

    **Posts Analyzed:**
    *   [200+ pages of Hugging Face secrets on how to train an LLM](https://reddit.com/r/LocalLLaMA/comments/1ok3xie/200_pages_of_hugging_face_secrets_on_how_to_train/)
    *   [Qwen 3 VL merged into llama.cpp!](https://reddit.com/r/LocalLLaMA/comments/1ok2lht/qwen_3_vl_merged_into_llamacpp/)
    *   [Kimi Linear released](https://reddit.com/r/LocalLLaMA/comments/1ojz8pz/kimi_linear_released/)
    *   [moonshotai/Kimi-Linear-48B-A3B-Instruct · Hugging Face](https://reddit.com/r/LocalLLaMA/comments/1ojzekg/moonshotaikimilinear48ba3binstruct_hugging_face/)
    *   [IBM just released unsloth for finetinuing Granite4.0\_350M](https://reddit.com/r/LocalLLaMA/comments/1okbrz4/ibm_just_released_unsloth_for_finetinuing/)
    *   [Faster llama.cpp ROCm performance for AMD RDNA3 (tested on Strix Halo/Ryzen AI Max 395)](https://reddit.com/r/LocalLLaMA/comments/1ok7hd4/faster_llamacpp_rocm_performance_for_amd_rdna3/)
    *   [Both Cursor and Cognition (Windsurf) new models are speculated to be built on Chinese base models?](https://reddit.com/r/LocalLLaMA/comments/1okppxs/both_cursor_and_cognition_windsurf_new_models_are/)
    *   [Another dim of scaling? ByteDance drops “Ouro”: 1.4B ≈ 4B, 2.6B ≈/＞ 8B](https://reddit.com/r/LocalLLaMA/comments/1okguct/another_dim_of_scaling_bytedance_drops_ouro_14b/)
    *   [Locally hosted Loveable with full stack support and llama.cpp, and more](https://reddit.com/r/LocalLLaMA/comments/1ok5rn2/locally_hosted_loveable_with_full_stack_support/)
    *   [support for Qwen3 VL has been merged into llama.cpp](https://reddit.com/r/LocalLLaMA/comments/1ok2kr3/support_for_qwen3_vl_has_been_merged_into_llamacpp/)
    *   [\[R\] We found LRMs look great…until the problems get harder (AACL 2025)](https://reddit.com/r/MachineLearning/comments/1okdq0s/r_we_found_lrms_look_greatuntil_the_problems_get/)
    *   [Developer vs Vibe Coding](https://reddit.com/r/OpenAI/comments/1ok34tz/developer_vs_vibe_coding/)
    *   [I build AI agents for a living. It's a mess out there.](https://reddit.com/r/AI_Agents/comments/1ojyu8p/i_build_ai_agents_for_a_living_its_a_mess_out/)
    *   [Claude wins today](https://reddit.com/r/ArtificialInteligence/comments/1oka4gy/claude_wins_today/)

    ### **Summary of Findings**

    The discussions reveal a rapidly evolving landscape for AI Engineers, marked by three key themes: a pivot towards architectural efficiency with models like **Kimi Linear** and **Ouro**; the maturation of the open-source ecosystem, particularly through community-driven tooling like **llama.cpp** and the rising influence of Chinese base models; and a growing dose of realism about the practical challenges of deploying AI agents in enterprise environments, where legacy systems and data quality are the primary bottlenecks.

    ---

    ### **Topic Analysis & Best Comments**

    #### **1. Emergence of Novel AI Architectures for Efficiency**
    There is significant excitement around new architectures that move beyond standard transformers to offer greater efficiency, especially for long-context tasks.

    *   **Models & Techniques:**
        *   **Kimi Linear (48B):** A hybrid linear attention model using a refined "Gated DeltaNet." It promises superior hardware efficiency by reducing KV cache needs by up to 75% and boosting decoding throughput up to 6x for 1M token contexts.
        *   **ByteDance Ouro:** A "Looped Language Model" that uses recurrent depth with shared weights to make smaller models perform like much larger ones (e.g., 2.6B model competing with 8B baselines on reasoning). This is achieved by having the model "think" iteratively over its own latent states.

    *   **Best Comments:**
        *   An insightful critique of dense architectures like Ouro: *"A side effect of making architectures more “dense” is that quantization becomes more damaging because the weights carry more genuine information and are thus more sensitive to truncation."*
        *   Connecting Ouro to previous research: *"This is similar to Universal Transformer/Mixture of recursions, and it was what allegedly gave HRM it's power. So I do firmly believe that's the future."*
        *   Explaining Kimi Linear's architecture: *"Modified Gated DeltaNet. For llama.cpp we will probably have to wait for the Qwen Next architecture implementation before having this one."*

    *   **Conflicting Opinions:** The performance of Kimi Linear is debated. One user provided benchmark charts suggesting it performs worse than the comparable Qwen3 model. However, other users countered this, arguing the benchmarks are misleading because Kimi was trained on significantly less data (5.7T vs 15T+ tokens) and that its subjective quality is superior: *"This is way superior to Qwen3-30B-A3B. Don't trust the benchmarks, just try it once you can."*

    #### **2. Maturation of Open-Source Models & Tooling**
    The open-source community continues to rapidly integrate new models and improve performance on consumer hardware, making powerful AI more accessible.

    *   **Models & Updates:**
        *   **Qwen 3 VL:** Support for this powerful vision-language model was merged into `llama.cpp`, a major event for the local AI community. The 32B text-only performance is seen as a significant upgrade over the previous Qwen3-32B checkpoint.
        *   **IBM Granite 4.0 (350M):** IBM partnered with Unsloth to release an optimized finetuning notebook for their small model, signaling a strong commitment from established Western companies to support the open-source ecosystem.
        *   **AMD ROCm Performance:** A community member developed and shared fixes for `llama.cpp` on AMD RDNA3 GPUs that significantly improve performance (up to 140% faster token generation) on long-context tasks, addressing a key pain point for AMD users.

    *   **Best Comments:**
        *   A quantitative comparison of Qwen 3 VL's text capabilities against previous text-only models, providing valuable benchmark data.
        *   A detailed technical bug report on Qwen 3 VL's OCR performance in `llama.cpp`, followed by a reply confirming a PR has been merged to fix it, showcasing the community's rapid development cycle.
        *   Praise for the developer behind the ROCm optimizations: *"people like you and your PR keep alive local inference for modest wallets and old hardware."*

    #### **3. Practical Realities of AI Implementation**
    Discussions from developers in the field provide a sober perspective on the challenges of deploying AI, particularly AI agents, in real-world business environments.

    *   **Project Ideas & Insights:**
        *   The post "I build AI agents for a living. It's a mess out there" highlights that the primary difficulty is not the AI model but integration with legacy systems (e.g., apps on Windows XP) and cleaning messy, unstructured data.
        *   The "Developer vs Vibe Coding" post sparked a debate about AI's impact on software development. The original post suggests AI-driven "vibe coding" is inefficient and leads to rewrites, while experienced developers in the comments argued that planning and architecture remain the most time-consuming parts, regardless of whether AI generates the code.

    *   **Best Comments:**
        *   A comment contextualizing the AI agent challenges within the broader history of tech: *"What you're talking about is basically the reality of the IT hype cycle...Business invest in the hype train instead of fixing their current problems...chasing hype is easier than doing the unsexy work of fixing broken foundations."*
        *   A classic but crucial reminder: *"Yes people seem to forget garbage in , garbage out. Ai doesn't magic it away."*
        *   On "vibe coding": *"I think it's important to draw a distinction between AI assisted development where you understand and check the code...vs AI driven development where you're just looking at the UI changes without seeing or understanding the code."*

    #### **4. Learning Resources & Advanced Techniques**
    Valuable educational materials and nuanced technical discussions provide deep dives for engineers looking to master LLM development.

    *   **Resources:**
        *   **Hugging Face's "Smol Training Playbook":** A comprehensive 200+ page guide from the HF pre-training team covering the entire LLM training pipeline, including what worked, what didn't, and infrastructure management.

    *   **Best Comments:**
        *   An insightful question on a specific technique from the Hugging Face playbook, questioning the practice of retaining reasoning tokens during training but not inference: *"...I would expect that this would lead to a less performant model at inference-time because every multi-turn conversation...is significantly out-of-distribution."* This is a high-level question about mitigating training/inference skew.

    ### **Key Insights & Trends**
    1.  **Architectural Innovation is Accelerating:** The industry is actively exploring alternatives to the standard Transformer architecture. Linear attention (Kimi Linear) and recurrent depth (Ouro) are key trends to watch for achieving performance parity with smaller, more efficient models. This shift impacts hardware requirements, quantization strategies, and inference optimization.

    2.  **The Open-Source Ecosystem is a Geopolitical Battleground:** There is a clear trend of US startups leveraging powerful, less-censored, and cost-effective open-weight models from Chinese companies (e.g., DeepSeek, GLM, Qwen). This is driven by a perceived lack of competitive, permissively licensed base models from Western companies, making Chinese models "budget kings" for building specialized products.

    3.  **Integration is the New Bottleneck:** For real-world AI applications, especially autonomous agents, the core challenge is shifting from model capability to systems integration. AI Engineers will increasingly need skills in data engineering, API integration, and navigating legacy enterprise software, as this is where most project time and complexity lie.

    4.  **Small Language Models (SLMs) are Gaining Serious Traction:** The push from companies like IBM with its Granite series, combined with efficient training tools like Unsloth, demonstrates a strong industry interest in developing and deploying highly capable small models for specialized tasks like customer support agents.

    5.  **Hardware-Specific Optimization Remains Crucial:** The community-driven performance improvements for AMD's ROCm stack in `llama.cpp` highlight that significant gains are still available through low-level software optimization. Expertise in CUDA, ROCm, and inference engines is a highly valuable skill for maximizing performance on consumer and enterprise hardware.""",
   config=types.GenerateContentConfig(
      response_modalities=["AUDIO"],
      speech_config=types.SpeechConfig(
         voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(
               voice_name='Sadaltager',
            )
         )
      ),
   )
)

data = response.candidates[0].content.parts[0].inline_data.data

file_name='out.wav'
wave_file(file_name, data) # Saves the file to current directory
