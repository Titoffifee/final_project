# **"Инвестиционный помощник**
## **О боте**
Бот предназначен для помощи инвесторам. Не выход из телеграмма можно получать котировки акций в онлайн режиме, анализировать нужные активы. 
Предоставляется возможность собирать их в портфель для более удобной работы
Также бот предоставляет возможность включать таймеры на активы, получая регулярные сообщения с измениями котировок
## **Архитектура и реализация**
### 1. main.py
Использует functions.py
Бот, сценарий и все обработчики
### 2. functions.py
Использует sql.py
Функции-помощиники и некоторые промежуточные звенья между сценариями, нужные для красивой реализации переходов, когда не приходит сообщения от пользователя
### 3. sql.py
Использует services.py
Классы и функции для подключения и работы с базой данных 
### 4. services.py
Константы, библиотеки и функции для работы с датами 

**Для более подробной информации о классе или методах следует обратиться к коду**
