# SmartBrew Email Automation System

A comprehensive email automation system for SmartBrew organization that simplifies email extraction, bulk sending, and campaign matching.

## Features

### 1. Email Extractor
- Extract emails from your inbox based on date and subject filters
- Process up to 3000+ emails at once
- Generate CSV reports with recipient details (Name, Email, Date, Frequency, Status)
- Track response status with visual analytics

### 2. Bulk Email Sender
- Send personalized emails to individual recipients or in bulk via CSV upload
- Choose from pre-configured templates or create custom emails
- Add attachments to your communications
- Include executive information for personalized signatures
- Track sending success rates with visual reports

### 3. Campaign Matcher
- Match sent emails with campaign follow-ups
- Filter based on executive CC inclusion
- Track response rates for specific campaigns
- Export data for detailed campaign analysis

## Screenshots

![Home Page](assets/home-screenshot.png)
![Email Extractor](assets/extractor-screenshot.png)
![Bulk Email Sender](assets/sender-screenshot.png)

## Project Structure

```
SmartBrew Email Project/
├── app.py                  # Main application entry point
├── requirements.txt        # Python dependencies
├── .env.template           # Environment variables template
├── README.md               # Project documentation
├── assets/                 # Static assets (images, etc.)
├── src/                    # Source code
│   ├── __init__.py
│   ├── components/         # UI components
│   │   ├── __init__.py
│   │   └── ui_components.py
│   ├── pages/              # Application pages
│   │   ├── __init__.py
│   │   ├── home_page.py
│   │   ├── email_extractor_page.py
│   │   ├── bulk_email_sender_page.py
│   │   └── campaign_matcher_page.py
│   ├── services/           # External services integration
│   │   └── __init__.py
│   └── utils/              # Utility functions
│       ├── __init__.py
│       ├── email_extractor.py
│       ├── email_sender.py
│       └── campaign_matcher.py
```

## Requirements

The application requires the following Python packages:
```
streamlit==1.30.0
pandas==2.1.3
plotly==5.18.0
imaplib2==3.06
email==4.0.2
matplotlib==3.8.2
numpy==1.26.3
pillow==10.1.0
python-dotenv==1.0.0
```

## Setup and Installation

1. Clone this repository
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
3. (Optional) Copy `.env.template` to `.env` and customize settings:
   ```
   cp .env.template .env
   ```
4. Run the Streamlit application:
   ```
   streamlit run app.py
   ```

## Email Security

This application requires your email credentials to function. We recommend using an app password (not your actual account password) for security. Here's how to generate an app password for Gmail:

1. Go to your Google Account settings (https://myaccount.google.com/)
2. Select "Security"
3. Turn on 2-Step Verification if not already activated
4. Under "Signing in to Google," select "App passwords"
5. Generate a new app password and use it in this application

## Usage Notes

- For bulk email sending, take a 60-minute break after sending 100 emails to avoid being flagged as spam.
- Your CSV file for bulk sending should include at minimum "Email" and "Name" columns.
- No credentials or personal data are stored in the application.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

Copyright © 2023 SmartBrew Email Automation System. All rights reserved.

## Support

For support, contact support@smartbrew.com "# SmartBrew-Email-Automation-System" 
