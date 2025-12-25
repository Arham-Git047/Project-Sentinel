
"""
Twilio Notification Service for Project Sentinel
Handles SMS and WhatsApp alerts for health threats
"""

import os
from twilio.rest import Client
from dotenv import load_dotenv
from typing import List, Optional, Dict
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

class TwilioNotificationService:
    """Handle SMS and WhatsApp notifications via Twilio"""
    
    def __init__(self):
        """Initialize Twilio client with credentials from .env"""
        
        # Load Twilio credentials
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.phone_number = os.getenv("TWILIO_PHONE_NUMBER")
        self.whatsapp_number = os.getenv("TWILIO_WHATSAPP_NUMBER")
        
        # Parse alert recipients (comma-separated in .env)
        self.alert_phones = self._parse_numbers(os.getenv("ALERT_PHONE_NUMBERS", ""))
        self.alert_whatsapp = self._parse_numbers(os.getenv("ALERT_WHATSAPP_NUMBERS", ""))
        
        # Initialize Twilio client
        self.client = None
        self.enabled = self._initialize_client()
    
    def _parse_numbers(self, numbers_str: str) -> List[str]:
        """Parse comma-separated phone numbers from .env"""
        if not numbers_str:
            return []
        return [num.strip() for num in numbers_str.split(",") if num.strip()]
    
    def _initialize_client(self) -> bool:
        """Initialize Twilio client and verify credentials"""
        
        # Check if all required credentials are present
        if not all([self.account_sid, self.auth_token, self.phone_number]):
            print("⚠️  Twilio credentials not configured")
            print("   Set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER in .env")
            print("   SMS/WhatsApp notifications: DISABLED")
            return False
        
        try:
            # Initialize Twilio client
            self.client = Client(self.account_sid, self.auth_token)
            
            # Test connection by fetching account info
            self.client.api.accounts(self.account_sid).fetch()
            
            # Success!
            print("✓ Twilio notifications: READY")
            print(f"   From Phone: {self.phone_number}")
            if self.whatsapp_number:
                print(f"   From WhatsApp: {self.whatsapp_number}")
            print(f"   SMS recipients: {len(self.alert_phones)}")
            print(f"   WhatsApp recipients: {len(self.alert_whatsapp)}")
            
            return True
            
        except Exception as e:
            print(f"⚠️  Twilio initialization failed: {e}")
            print("   SMS/WhatsApp notifications: DISABLED")
            return False
    
    def send_alert_sms(self, alert_data: dict) -> Dict:
        """
        Send SMS alert to configured recipients
        
        Args:
            alert_data: Dictionary containing alert information
            
        Returns:
            Dictionary with send results
        """
        if not self.enabled:
            return {
                "sent": False,
                "reason": "Twilio not configured"
            }
        
        if not self.alert_phones:
            return {
                "sent": False,
                "reason": "No SMS recipients configured"
            }
        
        # Format alert message for SMS
        message = self._format_alert_message(alert_data)
        
        results = []
        for phone in self.alert_phones:
            try:
                # Send SMS via Twilio
                msg = self.client.messages.create(
                    body=message,
                    from_=self.phone_number,
                    to=phone
                )
                
                results.append({
                    "to": phone,
                    "status": msg.status,
                    "sid": msg.sid,
                    "success": True
                })
                print(f"✓ SMS sent to {phone} (SID: {msg.sid[:10]}...)")
                
            except Exception as e:
                results.append({
                    "to": phone,
                    "error": str(e),
                    "success": False
                })
                print(f"✗ SMS failed to {phone}: {e}")
        
        return {
            "sent": True,
            "total_recipients": len(self.alert_phones),
            "successful": len([r for r in results if r.get("success")]),
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
    
    def send_alert_whatsapp(self, alert_data: dict) -> Dict:
        """
        Send WhatsApp alert to configured recipients
        
        Args:
            alert_data: Dictionary containing alert information
            
        Returns:
            Dictionary with send results
        """
        if not self.enabled:
            return {
                "sent": False,
                "reason": "Twilio not configured"
            }
        
        if not self.alert_whatsapp:
            return {
                "sent": False,
                "reason": "No WhatsApp recipients configured"
            }
        
        if not self.whatsapp_number:
            return {
                "sent": False,
                "reason": "TWILIO_WHATSAPP_NUMBER not configured"
            }
        
        # Format alert message for WhatsApp
        message = self._format_alert_message(alert_data)
        
        results = []
        for whatsapp in self.alert_whatsapp:
            try:
                # Send WhatsApp via Twilio
                msg = self.client.messages.create(
                    body=message,
                    from_=self.whatsapp_number,
                    to=whatsapp
                )
                
                results.append({
                    "to": whatsapp,
                    "status": msg.status,
                    "sid": msg.sid,
                    "success": True
                })
                print(f"✓ WhatsApp sent to {whatsapp} (SID: {msg.sid[:10]}...)")
                
            except Exception as e:
                results.append({
                    "to": whatsapp,
                    "error": str(e),
                    "success": False
                })
                print(f"✗ WhatsApp failed to {whatsapp}: {e}")
        
        return {
            "sent": True,
            "total_recipients": len(self.alert_whatsapp),
            "successful": len([r for r in results if r.get("success")]),
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
    
    def _format_alert_message(self, alert_data: dict) -> str:
        """
        Format alert data into SMS/WhatsApp message
        
        Args:
            alert_data: Dictionary with alert information
            
        Returns:
            Formatted message string
        """
        severity = alert_data.get('severity', 'UNKNOWN').upper()
        threat_type = alert_data.get('threat_type', 'Unknown').replace('_', ' ').title()
        zones = ', '.join(alert_data.get('affected_zones', ['Unknown']))
        confidence = alert_data.get('confidence', 0)
        description = alert_data.get('description', 'No description available')
        recommendations = alert_data.get('recommendations', [])
        
        # Build message
        message = f"""🚨 PROJECT SENTINEL ALERT

Severity: {severity}
Threat: {threat_type}
Location: {zones}
Confidence: {confidence:.1f}%

{description}

IMMEDIATE ACTIONS:
"""
        
        # Add top 3 recommendations
        for i, rec in enumerate(recommendations[:3], 1):
            # Remove emoji if present (some SMS systems don't support)
            clean_rec = ''.join(c for c in rec if c.isalnum() or c.isspace() or c in '.,!?-')
            message += f"{i}. {clean_rec}\n"
        
        message += "\n- Project Sentinel v3.0"
        
        return message
    
    def send_test_notification(self) -> Dict:
        """
        Send test notification to verify Twilio setup
        
        Returns:
            Dictionary with test results
        """
        if not self.enabled:
            return {
                "success": False,
                "message": "Twilio not configured. Check .env file."
            }
        
        test_message = """🛡️ Project Sentinel Test

This is a test notification from your health surveillance system.

If you received this message, SMS/WhatsApp notifications are working correctly!

System: Project Sentinel v3.0
Status: Operational"""
        
        results = {
            "sms": [],
            "whatsapp": []
        }
        
        # Test SMS
        if self.alert_phones:
            for phone in self.alert_phones:
                try:
                    msg = self.client.messages.create(
                        body=test_message,
                        from_=self.phone_number,
                        to=phone
                    )
                    results["sms"].append({
                        "to": phone,
                        "status": "sent",
                        "sid": msg.sid,
                        "success": True
                    })
                    print(f"✓ Test SMS sent to {phone}")
                except Exception as e:
                    results["sms"].append({
                        "to": phone,
                        "error": str(e),
                        "success": False
                    })
                    print(f"✗ Test SMS failed to {phone}: {e}")
        
        # Test WhatsApp
        if self.alert_whatsapp and self.whatsapp_number:
            for whatsapp in self.alert_whatsapp:
                try:
                    msg = self.client.messages.create(
                        body=test_message,
                        from_=self.whatsapp_number,
                        to=whatsapp
                    )
                    results["whatsapp"].append({
                        "to": whatsapp,
                        "status": "sent",
                        "sid": msg.sid,
                        "success": True
                    })
                    print(f"✓ Test WhatsApp sent to {whatsapp}")
                except Exception as e:
                    results["whatsapp"].append({
                        "to": whatsapp,
                        "error": str(e),
                        "success": False
                    })
                    print(f"✗ Test WhatsApp failed to {whatsapp}: {e}")
        
        return {
            "success": True,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        """
        Get notification service status
        
        Returns:
            Dictionary with service status
        """
        return {
            "enabled": self.enabled,
            "sms_recipients": len(self.alert_phones),
            "whatsapp_recipients": len(self.alert_whatsapp),
            "phone_number": self.phone_number if self.enabled else None,
            "whatsapp_number": self.whatsapp_number if self.enabled else None,
            "account_sid": self.account_sid[:10] + "..." if self.account_sid else None
        }

# Global notification service instance
notification_service = TwilioNotificationService()

