"""
Numerical codes for `syslog` facilities.

These constants in this module correspond to those defined in section 4.1.1 of
[RFC 3164](https://datatracker.ietf.org/doc/html/rfc3164#section-4.1.1).
"""

KERNEL = 0
"""Kernel messages"""

USER = 1
"""User-level messages"""

MAIL = 2
"""Mail system"""

SYSTEM_DAEMON = 3
"""System daemons"""

SECURITY_4 = 4
"""
Security/authorization messages

Various operating systems have been found to utilize Facilities 4, 10, 13 and 14
for security/authorization, audit, and alert messages which seem to be similar.
"""

SYSLOGD = 5
"""Messages generated internally by syslogd"""

LINE_PRINTER = 6
"""Line printer subsystem"""

NETWORK_NEWS = 7
"""Network news subsystem"""

UUCP = 8
"""UUCP subsystem"""

CLOCK_DAEMON_9 = 9
"""
Clock daemon

Various operating systems have been found to utilize both Facilities 9 and 15
for clock (cron/at) messages.
"""

SECURITY_10 = 10
"""
Security/authorization messages

Various operating systems have been found to utilize Facilities 4, 10, 13 and 14
for security/authorization, audit, and alert messages which seem to be similar.
"""

FTP_DAEMON = 11
"""FTP daemon"""

NTP = 12
"""NTP subsystem"""

LOG_AUDIT = 13
"""
Log audit

Various operating systems have been found to utilize Facilities 4, 10, 13 and 14
for security/authorization, audit, and alert messages which seem to be similar.
"""

LOG_ALERT = 14
"""
Log alert

Various operating systems have been found to utilize Facilities 4, 10, 13 and 14
for security/authorization, audit, and alert messages which seem to be similar.
"""

CLOCK_DAEMON_15 = 15
"""
Clock daemon

Various operating systems have been found to utilize both Facilities 9 and 15
for clock (cron/at) messages.
"""

LOCAL_0 = 16
"""Local use 0  (local0)"""

LOCAL_1 = 17
"""Local use 1  (local1)"""

LOCAL_2 = 18
"""Local use 2  (local2)"""

LOCAL_3 = 19
"""Local use 3  (local3)"""

LOCAL_4 = 20
"""Local use 4  (local4)"""

LOCAL_5 = 21
"""Local use 5  (local5)"""

LOCAL_6 = 22
"""Local use 6  (local6)"""

LOCAL_7 = 23
"""Local use 7  (local7)"""
