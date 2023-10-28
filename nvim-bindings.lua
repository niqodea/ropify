vim.api.nvim_create_user_command('RopifyMove', function()
    local resource = vim.fn.expand('%')
    local offset = vim.fn.line2byte(vim.fn.line('.')) + vim.fn.col('.') - 1
    local command = 'ropify move ' .. resource .. ' ' .. offset
    vim.cmd('split | terminal ' .. command)
    vim.api.nvim_buf_set_option(0, 'buflisted', false)
end, {})

vim.api.nvim_create_user_command('RopifyShowImports', function()
    local name = vim.fn.expand('<cword>')
    local command = 'ropify show-imports ' .. name
    vim.cmd('split | terminal ' .. command)
    vim.api.nvim_buf_set_option(0, 'buflisted', false)
end, {})
