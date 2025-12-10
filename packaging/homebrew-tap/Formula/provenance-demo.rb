# Homebrew Formula for Provenance Demo
# To use: brew tap hollowsunhc/homebrew-tap && brew install black
#
# This template should be updated after first release:
# 1. Update the GitHub repository URL if the project is renamed
# 2. Replace the SHA256 with the value from the published SHA256SUMS
# 3. Update the version component in the download URL

class ProvenanceDemo < Formula
  desc "Demo CLI showcasing supply chain security and provenance attestation"
  homepage "https://github.com/hollowsunhc/black"
  url "https://github.com/hollowsunhc/black/releases/download/v0.1.0/black.pyz"
  sha256 "REPLACE_WITH_SHA256_FROM_RELEASE"
  license "MIT"

  depends_on "python@3.11"

  def install
    # Install the .pyz file
    bin.install "black.pyz" => "black"
  end

  def caveats
    <<~EOS
      🎉 black has been installed!

      Quick Start:
        black --version
        black hello world

      Verify Installation Security:
        # Download the latest release artifacts
        gh release download v0.1.0 --repo hollowsunhc/black

        # Run 14-check verification
        export GITHUB_REPOSITORY=hollowsunhc/black
        black verify

      To install required verification tools (optional):
        brew install cosign gh osv-scanner

      Documentation:
        • Quick Start Guide: https://github.com/hollowsunhc/black/blob/main/docs/distribution/quickstart/HOMEBREW.md
        • Verification Example: https://github.com/hollowsunhc/black/blob/main/docs/security/VERIFICATION-EXAMPLE.md
        • Platform Support: https://github.com/hollowsunhc/black/blob/main/docs/distribution/PLATFORM-SUPPORT.md

      Upgrade:
        brew upgrade black

      Questions or Issues:
        https://github.com/hollowsunhc/black/issues
    EOS
  end

  test do
    system "#{bin}/black", "--version"
    system "#{bin}/black", "hello", "world"
  end
end
