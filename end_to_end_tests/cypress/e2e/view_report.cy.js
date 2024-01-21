describe('template spec', () => {

    beforeEach(() => {
        cy.fixture('user').then(user => {
            cy.register_user(user.username, user.password);
            cy.login_user(user.username, user.password);
        });
    });

    it('View Report Test', () => {
        cy.fixture('article').then(article => {
            var tags_list;

            cy.visit('http://127.0.0.1:8000/user_app/create_article/');

            tags_list = '';
            article.tags.forEach((tag) => {
                if (tags_list === '') {
                    tags_list = tag;
                } else {
                    tags_list += ', ' + tag;
                }
            });

            cy.get('#id_title').type(article.title);
            cy.get('#id_tags').type(tags_list);

            cy.get('#id_form-0-title').type(article.steps[0].title);
            cy.get('#id_form-0-description1').type(article.steps[0].description1);
            cy.get('#id_form-0-description2').type(article.steps[0].description2);

            cy.get('#add-step-button').click();

            cy.get('#id_form-1-title').type(article.steps[1].title);
            cy.get('#id_form-1-description1').type(article.steps[1].description1);
            cy.get('#id_form-1-description2').type(article.steps[1].description2);

            cy.get('button[type="submit"]').click();

            cy.visit('http://127.0.0.1:8000/user_app/user_panel/');

            cy.get('.card-body').should('contain', article.title);
            cy.get('.card-body').should('contain', 'Steps: 2');
            cy.fixture('user').then(user => {
                cy.get('.card-body').should('contain', user.username);
            });
            article.tags.forEach((tag) => {
                cy.get('.card-body').should('contain', '#' + tag);
            });
        });

        cy.visit('http://127.0.0.1:8000/user_app/user_panel/');

        cy.fixture('user').then(user => {
            cy.get('.card-body').should('contain', user.username);
        });

        cy.get('.card-body').should('contain', 'Status: na opened');

        cy.get('button[name="view_report"]').click();

        cy.fixture('article').then(article => {
            cy.get('h2').should('contain', 'Review "' + article.title + '"');
            cy.get('p').should('contain', 'Review new article "' + article.title + '"');
        });

        cy.get('.author').should('contain', 'system_automat');
        cy.get('.left-text').should('contain', 'na opened');

        cy.get('img[alt="Report Image"]')
            .should('exist')
            .and('have.attr', 'src')
            .and((src) => {
                expect(src).to.match(/favicon.*\.png$/);
            });

    });

    afterEach(() => {
        cy.visit('http://127.0.0.1:8000/registration/logout');
        cy.fixture('user').then(user => {
            cy.cleanup_user(user.username);
        });
    });
});