from pathlib import Path
import yaml
import unittest

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "showroom/content/modules/ROOT/pages"



class ParticipantExperienceTests(unittest.TestCase):
    def test_every_playbook_packages_the_partnership_skin_and_execute_bridge(self):
        for path in (ROOT / "default-site.yml", ROOT / "showroom/default-site.yml"):
            if not path.exists():
                continue
            config = yaml.safe_load(path.read_text())
            assert "supplemental_files" in config["ui"]
            skin = path.parent / config["ui"]["supplemental_files"]
            header = (skin / "partials/header-content.hbs").read_text()
            bridge = (skin / "js/vendor/clipboard.js").read_text()
            assert "redhat-logo.svg" in header and "intel-logo.svg" in header
            assert 'iframe[src*="/terminal"]' in bridge
            assert ".tabcontent.active" not in bridge


    def test_guides_do_not_require_untrusted_route_tls_for_local_fixtures(self):
        if ROOT.name not in {"virtualization-ai-401", "virtualization-ai-501"}:
            return
        page = (PAGES / "index.adoc").read_text()
        assert 'export PRESENTATION_URL="http://' in page
        assert ' -k ' not in page


    def test_permission_denial_is_safe_with_strict_shell_handling(self):
        if ROOT.name not in {"virtualization-ai-201", "virtualization-ai-301"}:
            return
        page = next(PAGES.glob("07-*.adoc")).read_text()
        assert 'oc auth can-i delete namespaces || true' in page
        assert 'test "$NAMESPACE_DELETE_ALLOWED" = "no"' in page


    def test_201_bootstraps_the_pinned_repository_before_relative_commands(self):
        if ROOT.name != "virtualization-ai-201":
            return
        page = (PAGES / "01-prerequisite.adoc").read_text()
        assert 'SOURCE_REVISION="{content_revision}"' in page
        assert 'git -C "$LAB_REPO" fetch --depth 1 origin "$SOURCE_REVISION"' in page
        assert 'cd "$LAB_REPO"' in page
        assert page.index('cd "$LAB_REPO"') < page.index("git rev-parse HEAD")


    def test_201_prepares_the_terminal_request_used_by_the_unavailable_condition(self):
        if ROOT.name != "virtualization-ai-201":
            return
        page = (PAGES / "06-break.adoc").read_text()
        assert 'contracts/examples/qualified-request.json' in page
        assert page.index('contracts/examples/qualified-request.json') < page.index('--data-binary')
