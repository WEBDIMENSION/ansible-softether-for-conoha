require 'spec_helper'

describe package do
  describe service('sshd') do
    it { should be_enabled }
    it { should be_running }
  end
end
