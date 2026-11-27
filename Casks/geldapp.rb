# frozen_string_literal: true

cask "geldapp" do
  version "0.3.0"
  sha256 "d5b1089642d18fa531368210b2685ed3a6e789fbf55e248966c7447f96b172bb"

  url "https://github.com/GeldApp/GeldApp/releases/download/v#{version}/GeldApp-#{version}-macos-universal.dmg"
  name "GeldApp"
  desc "Personal finance workspace"
  homepage "https://github.com/GeldApp/GeldApp"

  depends_on macos: :ventura

  app "GeldApp.app"

  caveats "Requires macOS 13.3 or later. The app cannot launch on macOS 13.0 through 13.2."
end
