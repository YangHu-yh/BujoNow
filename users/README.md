# Users Directory

This directory stores user-specific data for the BujoNow application.

## Structure

Each user's data is stored in a separate directory, identified by their Hugging Face username or ID:

```
users/
  ├── user1/
  │   ├── user_data.json       # User account information
  │   ├── journals/            # User's journal entries
  │   ├── uploads/             # User's uploaded files
  │   └── visualizations/      # User's visualization files
  ├── user2/
  │   ├── user_data.json
  │   ├── journals/
  │   ├── uploads/
  │   └── visualizations/
  └── ...
```

## Privacy

All user data is private and can only be accessed by the authenticated user. The application enforces this privacy by:

1. Using Hugging Face OAuth for authentication
2. Validating user sessions before accessing any user data
3. Storing user data in separate directories
4. Never sharing data between users

## Data Storage

- `user_data.json`: Contains user profile information and authentication data
- `journals/`: Contains journal entries organized by year and month
- `uploads/`: Contains files uploaded by the user (images, audio)
- `visualizations/`: Contains generated visualizations for the user

This directory structure is automatically created when a user first signs in to the application. 