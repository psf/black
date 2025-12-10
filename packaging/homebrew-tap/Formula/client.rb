# Homebrew Formula for black
# This is a template - customize for your needs

class Client < Formula
  desc "black - Demo CLI showcasing supply chain security and provenance"
  homepage "https://github.com/hollowsunhc/black"
  url "https://github.com/hollowsunhc/black/releases/download/v0.1.0/black.pyz"
  sha256 "REPLACE_WITH_ACTUAL_SHA256"
  license "MIT"

  def install
    bin.install "black.pyz" => "demo"
  end

  test do
    system "#{bin}/demo", "--version"
  end
end
