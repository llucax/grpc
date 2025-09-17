# Copyright 2016 gRPC authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Tests of credentials."""

import logging
import unittest

import grpc


class CredentialsTest(unittest.TestCase):
    def test_call_credentials_composition(self):
        first = grpc.access_token_call_credentials("abc")
        second = grpc.access_token_call_credentials("def")
        third = grpc.access_token_call_credentials("ghi")

        first_and_second = grpc.composite_call_credentials(first, second)
        first_second_and_third = grpc.composite_call_credentials(
            first, second, third
        )

        self.assertIsInstance(first_and_second, grpc.CallCredentials)
        self.assertIsInstance(first_second_and_third, grpc.CallCredentials)

    def test_channel_credentials_composition(self):
        first_call_credentials = grpc.access_token_call_credentials("abc")
        second_call_credentials = grpc.access_token_call_credentials("def")
        third_call_credentials = grpc.access_token_call_credentials("ghi")
        channel_credentials = grpc.ssl_channel_credentials()

        channel_and_first = grpc.composite_channel_credentials(
            channel_credentials, first_call_credentials
        )
        channel_first_and_second = grpc.composite_channel_credentials(
            channel_credentials, first_call_credentials, second_call_credentials
        )
        channel_first_second_and_third = grpc.composite_channel_credentials(
            channel_credentials,
            first_call_credentials,
            second_call_credentials,
            third_call_credentials,
        )

        self.assertIsInstance(channel_and_first, grpc.ChannelCredentials)
        self.assertIsInstance(channel_first_and_second, grpc.ChannelCredentials)
        self.assertIsInstance(
            channel_first_second_and_third, grpc.ChannelCredentials
        )

    def test_invalid_string_certificate(self):
        self.assertRaises(
            TypeError,
            grpc.ssl_channel_credentials,
            root_certificates="A Certificate",
            private_key=None,
            certificate_chain=None,
        )

    def test_ssl_credentials_with_incomplete_key_cert_pair(self):
        """Test that incomplete key-cert pairs raise ValueError instead of crashing."""
        # Test case 1: certificate_chain provided but private_key is None
        with self.assertRaises(ValueError) as cm:
            grpc.ssl_channel_credentials(certificate_chain=b"cert")
        self.assertIn("private_key must be provided", str(cm.exception))

        # Test case 2: private_key provided but certificate_chain is None  
        with self.assertRaises(ValueError) as cm:
            grpc.ssl_channel_credentials(private_key=b"key")
        self.assertIn("certificate_chain must be provided", str(cm.exception))

        # Test case 3: certificate_chain as empty bytes but private_key is None
        with self.assertRaises(ValueError) as cm:
            grpc.ssl_channel_credentials(certificate_chain=b"")
        self.assertIn("private_key must be provided", str(cm.exception))

        # Test case 4: private_key as empty bytes but certificate_chain is None
        with self.assertRaises(ValueError) as cm:
            grpc.ssl_channel_credentials(private_key=b"")
        self.assertIn("certificate_chain must be provided", str(cm.exception))

    def test_ssl_credentials_valid_combinations(self):
        """Test that valid combinations of SSL credentials work without errors."""
        # Test case 1: Both private_key and certificate_chain are None (should work)
        creds1 = grpc.ssl_channel_credentials()
        self.assertIsInstance(creds1, grpc.ChannelCredentials)

        # Test case 2: Both private_key and certificate_chain are provided (should work)
        creds2 = grpc.ssl_channel_credentials(
            private_key=b"fake_private_key",
            certificate_chain=b"fake_certificate_chain"
        )
        self.assertIsInstance(creds2, grpc.ChannelCredentials)

        # Test case 3: Only root_certificates provided (should work)
        creds3 = grpc.ssl_channel_credentials(
            root_certificates=b"fake_root_certs"
        )
        self.assertIsInstance(creds3, grpc.ChannelCredentials)

        # Test case 4: All parameters provided (should work)
        creds4 = grpc.ssl_channel_credentials(
            root_certificates=b"fake_root_certs",
            private_key=b"fake_private_key", 
            certificate_chain=b"fake_certificate_chain"
        )
        self.assertIsInstance(creds4, grpc.ChannelCredentials)


if __name__ == "__main__":
    logging.basicConfig()
    unittest.main(verbosity=2)
