# SWA Crew Quest: Trivia & Training

✈️ 🎯 💫 An interactive training and trivia application designed specifically for Southwest Airlines crew members, celebrating the spirit of SWA while enhancing professional knowledge through engaging scenarios.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://swaquest.streamlit.app)

## Features

- **Role-Specific Training**: Customized scenarios for different SWA roles including Flight Attendants, Pilots, Ground Operations, and more
- **Dynamic Content Generation**: Uses Google's Gemini AI to create unique, relevant scenarios and questions
- **Interactive Learning**: Engaging trivia and real-world scenarios that test and enhance professional knowledge
- **Performance Tracking**: Leaderboard system to track and celebrate top performers
- **Adaptive Difficulty**: Questions ranging from easy to challenging across various aviation categories
- **Categories Covered**:
  - Customer Service
  - Operations
  - Company Culture
  - Aviation History
  - Technical Knowledge
  - Problem Solving
  - Leadership
  - And more!

## Installation

1. Clone the repository:
```bash
git clone https://github.com/lhiebert01/swaquest.git
cd swaquest
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

1. Create a `.env` file in the project root:
```env
GEMINI_API_KEY=your_gemini_api_key
```

2. For Streamlit deployment:
   - Add your API key to Streamlit secrets
   - Format: `GEMINI_API_KEY = "your_key_here"`

## Usage

1. Run locally:
```bash
streamlit run app.py
```

2. Enter your name and optionally select your SWA role
3. Complete scenarios and answer questions
4. Track your progress on the leaderboard
5. Learn from detailed explanations and aviation facts

## Development

- Built with Streamlit and Google's Gemini AI
- Implements session state management for seamless user experience
- Features role-specific content generation
- Includes comprehensive error handling

## Deployment

The app is deployed on Streamlit Cloud. For deployment:

1. Push to GitHub
2. Connect repository to Streamlit Cloud
3. Configure environment variables
4. Deploy!

## Security

- API keys and sensitive data managed through Streamlit secrets
- Secure handling of user information
- No personal data stored or transmitted

## Credits

Developed by [Lindsay Hiebert](https://www.linkedin.com/in/lindsayhiebert/), a Generative AI expert creating applications focused on the health, happiness, and growth of people.

## Feedback

Connect with me on [LinkedIn](https://www.linkedin.com/in/lindsayhiebert/) to share your thoughts or discuss AI solutions that make a difference.

## License & Rights

This project is licensed under the MIT License, with the following additional terms:

© 2024 Lindsay Hiebert. All Rights Reserved.

This application is currently in beta and is a proprietary training solution that may be offered commercially in the future. While the code is shared under the MIT License, all rights to the commercial application, its design patterns, and training methodologies are reserved. Any use, modification, or distribution of this code must maintain this attribution and rights notice.

Commercial use or deployment of this application or substantially similar training systems requires explicit written permission from the author.

## Credits

Developed by [Lindsay Hiebert](https://www.linkedin.com/in/lindsayhiebert/), a Generative AI expert creating applications focused on the health, happiness, and growth of people. This application represents a beta version of a potential commercial training solution.

## Feedback & Commercial Inquiries

- Connect with me on [LinkedIn](https://www.linkedin.com/in/lindsayhiebert/) to share your thoughts or discuss AI solutions that make a difference
- For commercial licensing or deployment inquiries, please reach out through LinkedIn
- Beta testing feedback is welcome and appreciated