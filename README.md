Если вы сталкиваетесь с проблемами при запуске,
то напишите, пожалуйста, на один из этих аккаунтов в телеграме: @ilyamikhailov16, @RenarinZero, @whiskeygerman, @twirlz, @developersnap

Для использования ИИ на платформе предусмотрено два варианта. 
Но для начала вам необходимо создать .env файл -> смотрите env.template

## Онлайн-режим:
*   Регистрация на OpenRouter и получение API токена -> его необходимо будет вставить в .env
*   Здесь же необходимо прописать путь(или задать его в app/config/config.py) к модели с OpenRouter, которую вы хотите использовать
    (По умолчанию: "qwen/qwen3-14b:free")

## Локал-режим:
*   Используется llama_cpp и необходимо иметь скачанный .gguf файл с моделью у себя на компьютере.
    К примеру - https://huggingface.co/Volko76/Qwen2.5-Coder-1.5B-Instruct-GGUF?show_file_info=qwen2.5-coder-1.5b-instruct.Q8_0.gguf

*   для установки llama_cpp пропишите команду llama-cpp-python в терминале

*   если выдает ошибку ERROR: Failed building wheel for llama-cpp-python(или другую похожую), 
    то качайте https://visualstudio.microsoft.com/visual-cpp-build-tools/, выбирайте 
    "Разработка классических приложений на c++" в установщике и пакеты: CMake, MSVC v143 – VS 2022 C++ x64/x86 build tools,
    Windows SDK, English language pack

*   Далее необходимо создать папку local_models в главной директории и вложить туда .gguf файл

*   Также необходимо прописать имя файла .gguf в .env(или в config.py)

*   Смотрите app/config/config.py, чтобы понимать возможности конфигурации и какие переменные прописывать в .env
    (для конфигурации используется библиотека pydantic)

*   Онлайн режим устанвлен по умолчанию, для локала также необходимо прописать в .env:
    CONFIG__DEFAULTSCONFIG__MODEL_TYPE = "local"

Всё, что можно прописать в .env, можно прописать и напрямую через config.py