# SPDX-License-Identifier: Apache-2.0
#
# The OpenSearch Contributors require contributions made to
# this file be licensed under the Apache-2.0 license or a
# compatible open source license.

import os
import unittest
from unittest.mock import MagicMock

from assemble_workflow.bundle import Bundle
from manifests.build_manifest import BuildManifest


class TestBundle(unittest.TestCase):
    class DummyBundle(Bundle):
        def install_plugin(self, plugin):
            pass

    def test_bundle(self):
        manifest_path = os.path.join(
            os.path.dirname(__file__), "data/opensearch-build-1.1.0.yml"
        )
        artifacts_path = os.path.join(os.path.dirname(__file__), "data/artifacts")
        bundle = self.DummyBundle(
            BuildManifest.from_path(manifest_path), artifacts_path, MagicMock()
        )
        self.assertEqual(bundle.min_tarball.name, "OpenSearch")
        self.assertEqual(len(bundle.plugins), 12)
        self.assertEqual(bundle.artifacts_dir, artifacts_path)
        self.assertIsNotNone(bundle.bundle_recorder)
        self.assertEqual(bundle.installed_plugins, [])
        self.assertTrue(
            bundle.min_tarball_path.endswith("/opensearch-min-1.1.0-linux-x64.tar.gz")
        )
        self.assertIsNotNone(bundle.archive_path)

    def test_bundle_does_not_exist_raises_error(self):
        manifest_path = os.path.join(
            os.path.dirname(__file__), "data/opensearch-build-1.1.0.yml"
        )
        with self.assertRaisesRegex(
            FileNotFoundError,
            "does-not-exist/bundle/opensearch-min-1.1.0-linux-x64.tar.gz",
        ):
            self.DummyBundle(
                BuildManifest.from_path(manifest_path),
                os.path.join(os.path.dirname(__file__), "data/does-not-exist"),
                MagicMock(),
            )

    def test_bundle_invalid_archive_raises_error(self):
        manifest_path = os.path.join(
            os.path.dirname(__file__), "data/opensearch-build-1.1.0.yml"
        )
        with self.assertRaisesRegex(FileNotFoundError, "(/*)$"):
            self.DummyBundle(
                BuildManifest.from_path(manifest_path),
                os.path.join(os.path.dirname(__file__), "data/invalid"),
                MagicMock(),
            )
