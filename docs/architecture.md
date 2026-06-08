graph TB
    subgraph FE ["Frontend — React (Vite)"]
        Chat["Chat UI\n• File attach (PDF)\n• Word download card (.docx)"]
        Admin["Admin UI\n• Skills Manager\n• Tools Manager"]
    end

    subgraph API ["FastAPI Backend :8000"]
        Routes["routes.py\nPOST /api/chat\nGET /api/skills (read-only)\nGET /api/tools (read-only)"]
        CVRoutes["cv_routes.py\nGET /api/cv/download-word/{id}"]
    end

    subgraph LG ["LangGraph Workflow — ReAct Pattern"]
        direction LR
        S([START]) --> LLM
        LLM["llm_node\n_build_system_prompt()\nBASE_PROMPT + CATALOG skill (name+desc)"]
        LLM -->|"has tool_calls"| TN["ToolNode"]
        TN -->|"re-entry"| LLM
        LLM -->|"no tool_calls"| E([END])
    end

    subgraph SKILLS ["Skill System — Progressive Disclosure (nguồn: MinIO)"]
        SR[("SkillRegistry\nTTL cache RAM\nlist_all()/get()")]
        MINIO[("MinIO bucket 'skills'\n*.md (frontmatter + body)")]
        SEED["seed: skills/library/*.md\n(git → sync_skills_to_minio.py)"]
    end

    subgraph TOOLS ["Tool Registry — 8 tools"]
        CT["company_tools.py\n• get_company_info\n• get_current_datetime\n• calculate\n• get_company_employee_list\n• get_demo_users_list"]
        CVT["cv_tools.py\n• read_cv_file\n• generate_cv_word_file (template_id 1|2) → __docx_id__"]
        ST["skill_tools.py\n• load_skill (nạp body on-demand)"]
    end

    subgraph STORE ["Storage"]
        DB[("SQLite\ndata/company.db")]
        MEM[("In-Memory\n_pdf_store — xóa sau request\n_cv_docx_store ⚠️ no TTL")]
    end

    subgraph EXT ["External"]
        LLMProxy["9Router LLM Proxy\n172.31.2.23:20128/v1\nmodel: evotek_flash"]
        DemoAPI["Demo Users API\n127.0.0.1:8080"]
    end

    Chat -->|"FormData: user_id, query, file?"| Routes
    Admin -->|REST| Routes
    Chat -->|"tải .docx"| CVRoutes

    Routes -->|"chatbot.ainvoke()"| LG
    Routes -->|"detect markers\npost-process"| MEM

    LLM -->|"ChatOpenAI API"| LLMProxy
    LLM -->|"catalog name+desc"| SR
    SR -->|"refresh theo TTL"| MINIO
    SEED -.->|"upload .md"| MINIO
    ST -->|"get(name).body"| SR

    TN --> TOOLS
    CT --> DB
    CT -->|"HTTP GET"| DemoAPI
    CVT --> MEM
    CVT -->|"extract_cv_data"| LLMProxy

    CVRoutes -->|"đọc _cv_docx_store"| MEM

    Routes -->|"response + word_download_url"| Chat

    style MEM fill:#fff3cd,stroke:#ffc107
    style LLMProxy fill:#d1ecf1,stroke:#17a2b8
    style LG fill:#f8f9fa,stroke:#6c757d
    style SKILLS fill:#e8f5e9,stroke:#4caf50
    style MINIO fill:#fde2e4,stroke:#e63946