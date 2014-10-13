guard 'livereload' do
  watch(%r{.*/templates/.+\.html})
  watch(%r{.*/static/styles/.+\.css$})
  watch(%r{.*/static/scripts/.+\.js})
end

guard 'compass', :configuration_file => 'storm/frontend/scss/config.rb' do
  watch(%r{^storm/frontend/scss/(.*)\.s[ac]ss})
end

guard 'coffeescript', :input => 'storm/frontend/coffeescripts', :output => 'storm/frontend/static/scripts'

guard 'coffeedripper', :input => 'storm/frontend/beans', :output => 'storm/frontend/coffeescripts', :config => 'storm/frontend/coffeescripts/scripts.yml' do
  watch(%r{^storm/frontend/beans/(.+)\.bean$}) {|m| "#{m[1]}.bean"}
end
