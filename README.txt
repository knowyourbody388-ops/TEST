ADVANCE ARENA PRO - FULL STACK VERSION

What this version adds:
- Login and signup
- Real SQLite database: advance_arena.db
- Online account saving when hosted on a server
- Admin panel
- Mech Arena item database seed
- Goal tracker, calendar, rewards, analytics, mission status
- Images are embedded inside the HTML

HOW TO RUN ON YOUR COMPUTER

1. Extract this folder
2. Open the folder
3. Right-click inside the folder and open Terminal / CMD
4. Run:

   python server.py

5. Open browser:

   http://localhost:8000

DEFAULT ADMIN LOGIN

Username: admin
Password: admin123

Important:
- Change the admin password if you put this online.
- The database file will be created automatically as advance_arena.db
- Normal users can create accounts and their goals save in the database.
- Admin can see users and manage the item database.

TO PUT ONLINE

You need hosting that can run Python, such as a VPS, Render, Railway, Fly.io, or similar.
After hosting, the same database will save user accounts online.
