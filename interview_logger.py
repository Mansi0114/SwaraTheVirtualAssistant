"""
Interview session logging and export module for Swara.
Stores Q&A pairs and provides CSV export functionality.
"""
import csv
import os
import threading
from datetime import datetime


class InterviewLogger:
    """Manages interview session logging."""

    def __init__(self):
        self.sessions = []
        self.current_session = None
        self._lock = threading.Lock()

    def start_session(self, role):
        with self._lock:
            self.current_session = {
                'role': role,
                'start_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'qa_pairs': [],
                'feedback_items': []
            }
            self.sessions.append(self.current_session)

    def add_qa_pair(self, question, answer):
        with self._lock:
            if self.current_session:
                self.current_session['qa_pairs'].append({
                    'question': question,
                    'answer': answer,
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                })

    def add_feedback(self, feedback):
        with self._lock:
            if self.current_session:
                self.current_session['feedback_items'].append({
                    'feedback': feedback,
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                })

    def end_session(self):
        with self._lock:
            if self.current_session:
                self.current_session['end_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.current_session = None

    def export_to_csv(self, filename=None):
        if not self.sessions:
            return "No sessions to export."

        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"interview_session_{timestamp}.csv"

        try:
            os.makedirs('logs', exist_ok=True)
            filepath = os.path.join('logs', filename)

            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([
                    'Session Role', 'Start Time', 'End Time',
                    'Question', 'Answer', 'Session Feedback'
                ])

                for session in self.sessions:
                    role = session.get('role', '')
                    start_time = session.get('start_time', '')
                    end_time = session.get('end_time', '')
                    qa_pairs = session.get('qa_pairs', [])
                    feedback_items = session.get('feedback_items', [])

                    session_feedback = ""
                    if feedback_items:
                        session_feedback = feedback_items[-1].get('feedback', '')

                    if not qa_pairs:
                        writer.writerow([role, start_time, end_time, '', '', session_feedback])
                    else:
                        for i, qa in enumerate(qa_pairs):
                            writer.writerow([
                                role if i == 0 else '',
                                start_time if i == 0 else '',
                                end_time if i == 0 else '',
                                qa.get('question', ''),
                                qa.get('answer', ''),
                                session_feedback if i == 0 else ''
                            ])

            return f"Interview session exported to {filepath}."
        except Exception as e:
            return f"Error exporting session: {e}"

    def get_summary(self):
        if not self.sessions:
            return "No sessions recorded."

        summary = f"Total sessions: {len(self.sessions)}\n"
        for i, session in enumerate(self.sessions, 1):
            role = session.get('role', 'Unknown')
            qa_count = len(session.get('qa_pairs', []))
            summary += f"\nSession {i}: {role} - {qa_count} Q&A pairs"

        return summary


# Global logger instance
interview_logger = InterviewLogger()
