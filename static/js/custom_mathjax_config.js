window.MathJax = {
    options: {
        ignoreHtmlClass: 'tex2jax_ignore',
        processHtmlClass: 'tex2jax_process'
    },
    tex: {
        autoload: {
            color: [],
            colorv2: ['color']
        },
        packages: { '[+]': ['noerrors'] },
    },
    loader: {
        load: ['[tex]/noerrors']
    }
};
