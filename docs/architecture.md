graph TB
    subgraph FE ["Frontend — React (Vite)"]
        Chat["Chat UI\n• File attach (PDF)\n• Rich HTML card\n• Word download card"]
        Admin["Admin UI\n• Skills Manager\n• Tools Manager\n• CV Processor"]
    end

    subgraph API ["FastAPI Backend :8000"]
        Routes["routes.py\nPOST /api/chat\nGET /api/skills\nPOST /api/skills/draft\nPOST /api/skills/publish\nDELETE /api/skills"]
        CVRoutes["cv_routes.py\nPOST /api/cv/extract\nPOST /api/cv/render\nGET /api/cv/download-word/{id}"]
    end

    subgraph LG ["LangGraph Workflow — ReAct Pattern"]
        direction LR
        S([START]) --> LLM
        LLM["llm_node\n_build_system_prompt()\nBASE_PROMPT + tất cả skill prompts"]
        LLM -->|"has tool_calls"| TN["ToolNode"]
        TN -->|"re-entry"| LLM
        LLM -->|"no tool_calls"| E([END])
    end

    subgraph SKILLS ["Skill System — 1 tầng phẳng"]
        SR[("SkillRegistry\nlist_all() → inject vào llm_node")]
        JSON[("JSON Files\nstorage/custom_skills/\ncv_processor.json\n+ custom skills...")]
        SF["SkillFactory\ncreate_from_description()"]
    end

    subgraph TOOLS ["Tool Registry — 8 tools"]
        CT["company_tools.py\n• get_company_info\n• get_current_datetime\n• calculate\n• get_company_employee_list\n• get_demo_users_list"]
        CVT["cv_tools.py\n• read_cv_file\n• generate_cv_file → __html_id__\n• generate_cv_word_file → __docx_id__"]
    end

    subgraph STORE ["Storage"]
        DB[("SQLite\ndata/company.db")]
        MEM[("In-Memory\n_pdf_store — xóa sau request\n_cv_html_store ⚠️ no TTL\n_cv_docx_store ⚠️ no TTL")]
    end

    subgraph EXT ["External"]
        LLMProxy["9Router LLM Proxy\n172.31.2.23:20128/v1\nmodel: evotek_flash"]
        DemoAPI["Demo Users API\n127.0.0.1:8080"]
    end

    Chat -->|"FormData: user_id, query, file?"| Routes
    Admin -->|REST| Routes
    Admin -->|"PDF upload"| CVRoutes

    Routes -->|"chatbot.ainvoke()"| LG
    Routes -->|"detect markers\npost-process"| MEM

    LLM -->|"ChatOpenAI API"| LLMProxy
    LLM -->|"load all skills"| SR
    SR <-->|"read/write"| JSON
    Routes -->|"draft / publish"| SF
    SF -->|register| SR

    TN --> TOOLS
    CT --> DB
    CT -->|"HTTP GET"| DemoAPI
    CVT --> MEM

    CVRoutes -->|"extract + render"| LLMProxy
    CVRoutes --> MEM

    Routes -->|"response + rich_html\n+ word_download_url"| Chat

    style MEM fill:#fff3cd,stroke:#ffc107
    style LLMProxy fill:#d1ecf1,stroke:#17a2b8
    style LG fill:#f8f9fa,stroke:#6c757d
    style SKILLS fill:#e8f5e9,stroke:#4caf50